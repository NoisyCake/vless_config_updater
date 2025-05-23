import os
import time
import httpx
import base64
import asyncio
import logging
import logging.handlers
import aiofiles
import tempfile
from dotenv import load_dotenv
from shutil import rmtree

import utils
from parser import parse_vless_uri



logger_file = logging.handlers.TimedRotatingFileHandler(
    filename="logs/py.log",
    when="midnight",
    interval=1,
    backupCount=5,   # Keep up to 5 log files
    encoding="utf-8"
)
formatter = logging.Formatter(
    fmt='[{asctime}] #{levelname:8} {filename}:{lineno} - {message}',
    style='{'
)
logger_file.setFormatter(formatter)
logger = logging.getLogger()
logger.handlers.clear()
logger.setLevel(logging.DEBUG)
logger.addHandler(logger_file)

load_dotenv()



async def download_file(url: str, local_path: str) -> None:
    '''
    Downloads file with configurations from the GitHub or
    other source.\n
    Args:
        url: Web address of the source.
        local_path: Local path where the file will be located.
    '''
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            logger.info("File was successfully fetched")
        except httpx.HTTPStatusError as e:
            logger.critical(f"File fetch error {str(e)}")
            raise e
        
    async with aiofiles.open(local_path, 'w', encoding='utf-8') as file:
        await file.write(response.text)



async def measure_server_speed(proxy: str, timeout: int = 5) -> float:
    '''
    Measures download speed (Mbit/s) via running http-proxy.
    Uses chunked streaming for accuracy.
    Args:
        proxy: Proxy server address.
        timeout: Timeout.
    Returns speed in megabits per second.
    '''
    test_url = "https://speed.cloudflare.com/__down?bytes=25000000"

    
    try:
        async with httpx.AsyncClient(proxy=proxy, timeout=timeout) as client:
            start = time.perf_counter()
            total_bytes = 0
            
            async with client.stream("GET", test_url) as response:
                async for chunk in response.aiter_bytes():
                    total_bytes += len(chunk)
                    
            delta = time.perf_counter() - start
            speed_mbps = (total_bytes * 8) / (delta * 1_000_000)
            return speed_mbps
    except Exception as e:
        logger.warning("Unable to measure server speed")
        return 0.0
    


async def filter_configs(
    raw_configs_path: str,
    result_path: str,
    protocol: str = "vless"
) -> None:
    '''
    Filters configs in input file which are works.\n
    Uses sing-box as a client to connect to the server.
    Args:
        raw_configs_path: Local file with all configs.
        result_path: Local path where the filtered
            configs will be located.
        protocol: The name of the protocol to get.
    '''
    semaphore = asyncio.Semaphore(10)
    
    async with (
        aiofiles.open(result_path, 'w', encoding='utf-8') as output_file,
        aiofiles.open(raw_configs_path, encoding='utf-8') as input_file
    ):
    
        async def check_config(config_uri: str):
            '''
            Checks the config trying to connect to the
            proxy server via the sing-box.
            Args:
                config_uri: Config URI
            '''
            if not config_uri.startswith(protocol):
                return
            
            async with semaphore:
                port = utils.get_free_port()
                proxy = f"http://127.0.0.1:{port}"
                config_path = tempfile.mktemp(suffix='.json', dir='tmp/json_configs')
                
                async with httpx.AsyncClient(proxy=proxy, timeout=3) as client:
                    await parse_vless_uri(config_uri, config_path=config_path, http_port=port)
                
                    try:
                        # Starting sing-box
                        await asyncio.create_subprocess_exec("/app/sing-box", "run", "-c", config_path)
                        await asyncio.sleep(0.5)  # To make sure that the sing-box is running
                
                        response = await client.get("https://www.cloudflare.com")
                        response.raise_for_status()
                        
                        server_speed = await measure_server_speed(proxy)
                        logger.info(f"Server speed: {server_speed} - {config_uri.strip()}")
                        if server_speed < int(os.getenv('SPEED_LIMIT')):
                            logger.warning(f"Slow config: {config_uri.strip()}")
                            return
                        
                        await output_file.write(config_uri)
                        logger.info(f"Passed: {config_uri.strip()}")
                    
                    except httpx.HTTPError as e:
                        logger.warning(f"Non-working config: {config_uri.strip()}: {e}")
                    
                    finally:
                        os.remove(config_path)

        tasks = []
        async for line in input_file:
            tasks.append(check_config(line))
        
        await asyncio.gather(*tasks)
        logger.info("Configs have been written to the file")
        
        
        
async def update_file(url: str, local_path: str) -> None:
    '''
    Updates GitHub file.
    Args:
        url: Web address of the file.
        local_path: Local path where the result file located.
    '''
    async with httpx.AsyncClient(timeout=5) as client:
        headers = {
            "Authorization": f"token {os.getenv("GITHUB_TOKEN")}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        sha = response.json()["sha"]
        
        async with aiofiles.open(local_path, encoding='utf-8') as file:
            content =  await file.read()
            
        encoded_content = base64.b64encode(content.encode()).decode()
        
        payload = {
            "message": "Update config file",
            "content": encoded_content,
            "sha": sha,
            "branch": "main"
        }
        
        response = await client.put(url, headers=headers, json=payload)
        response.raise_for_status()
        logger.info("File was successfully updated")



async def main() -> None:    
    os.makedirs("tmp/json_configs", exist_ok=True)
    await download_file(os.getenv('STEAL_FROM'), "tmp/raw_configs.txt")
    await filter_configs("tmp/raw_configs.txt", "tmp/result.txt")
    await update_file(os.getenv("CONFIG_FILE_URL"), "tmp/result.txt")
    rmtree('tmp', ignore_errors=True)
    
if __name__ == '__main__':
    asyncio.run(main())
