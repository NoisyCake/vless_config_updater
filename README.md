<div align="center" markdown>

<p align="center">
    <a href="https://github.com/NoisyCake/vless_config_updater/blob/main/README.md"><u><b>ENGLISH</b></u></a> •
    <a href="https://github.com/NoisyCake/vless_config_updater/blob/main/README.ru.md"><u><b>РУССКИЙ</b></u></a>
</p>

# vless_config_updater

A background tool that pulls a public list of URI-like Xray/Sing-box configs and filters out only working VLESS entries.

A detailed description of the project is available on the [author's website](https://noisycake.ru/projects/vless_config_updater/)
</div>

## Install & Setup

> [!NOTE]
> For Debian-based Linux systems.

Download and install dependencies:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Download repo:
```bash
git clone https://github.com/NoisyCake/vless_config_updater.git
cd vless_config_updater
cp .env.example .env
chmod +x set_timer.sh
```

## Environment Variables
Edit .env with your own values:
|variable|description|example|
|:--:|:--|:--|
|STEAL_FROM|Public config source URL|https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Sub1.txt|
|CONFIG_FILE_URL|GitHub URL to push the result file|https://api.github.com/.../file.txt|
|GITHUB_TOKEN|GitHub access token (needed for private repos)|ghp_dhoauigc7898374yduisdhSDHFHGf7|
|SPEED_LIMIT|Min speed (Mbps) required for configs to be accepted|5|
|CONFIGS_LIMIT|Min number of valid configs needed to trigger a push|1|
|UPDATE_DELAY|How often (in minutes) the update should run|60|
|LOG_RETENTION_DAYS|How many days to keep logs before cleanup|7|

To fine-tune <SPEED_LIMIT>, run the script a few times, check `logs/py.log`, and look for lines like "Server speed: ...". Use the average or whatever makes sense for your use case.

---
## Run
To set up and start the timer-based job: `sudo ./set_timer.sh`. Run this again if you update `.env`.

The tool will auto-run every <UPDATE_DELAY> minutes and update the GitHub file.

To check the timer: `sudo systemctl status vless_config_updater.timer`. Look for the "Trigger:" line to see when the next run is scheduled.

---
## License

MIT licensed — see `LICENSE` for details.

---
## Changelog & Feedback

Suggestions, bug reports, and pull requests are welcome!
