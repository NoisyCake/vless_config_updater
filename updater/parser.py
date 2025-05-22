import json
import aiofiles
from urllib.parse import urlparse, parse_qs, unquote



async def parse_vless_uri(vless_uri: str, config_path: str, http_port: int) -> None:
    '''
    Makes json config file from VLESS URI. May not work correctly with come URI's.
    Args:
        vless_uri: VLESS URI.
        config_path: The path where the json config will be located.
        http_port: Free port for inbound http-proxy work.
    '''
    parsed = urlparse(vless_uri.strip())
    
    protocol = parsed.scheme
    uuid = parsed.username or parsed.netloc.split('@')[0]
    server = parsed.hostname
    server_port = parsed.port
    query = parse_qs(parsed.query)
    type = query.get('type', [''])[0]
    
    # Default values
    utls = {}
    reality = {}
    tls = {}
    transport = {}
    
    if type == 'tcp':
        security = query.get('security', [''])[0]
        sni = query.get('sni', [''])[0]

        if security == 'reality':
            pbk = query.get('pbk', [''])[0]
            fp = query.get('fp', [''])[0]
            sid = query.get('sid', [''])[0]
        
            utls = {
                'enabled': bool(pbk),
                'fingerprint': fp
            }
            reality = {
                'enabled': bool(pbk),
                'public_key': pbk,
                'short_id': sid
            }
            
        tls = {
            'enabled': bool(type),
            'server_name': sni,
        
            'utls': utls,
            'reality': reality
        }
        
    elif type == 'grpc':
        service_name = query.get("serviceName", [''])[0]
        
        transport = {
            "type": type,
            "service_name": service_name
        }
        
    elif type == 'ws':
        path = query.get("path", [''])[0]
        
        transport = {
            "type": type,
            "path": path
        }
        
    flow = query.get('flow', [''])[0]
    
    tag = unquote(parsed.fragment) if parsed.fragment else 'vless-out'

    

    outbounds = [
        {
            'type': protocol,
            'tag': tag,
            
            'server': server,
            'server_port': server_port,
            'uuid': uuid,
            'flow': flow,
            'tls': tls,
            'transport': transport
        }
    ]
    
    configuration = {
        'log': {
            'disabled': False,
            'level': "warn",
            'output': 'updater/logs/sing-box.log',
            'timestamp': True
        },
        'inbounds': [
            {
                'type': "http",
                'tag': "http-in",
                'listen': "127.0.0.1",
                'listen_port': http_port,
            }
        ],
        'outbounds': outbounds
    }

    async with aiofiles.open(config_path, 'w', encoding='utf-8') as file:
        data = json.dumps(configuration, indent=2)
        await file.write(data)