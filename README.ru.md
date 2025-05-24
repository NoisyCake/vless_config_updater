<div align="center" markdown>

<p align="center">
    <a href="https://github.com/NoisyCake/vless_config_updater/blob/main/README.md"><u><b>ENGLISH</b></u></a> •
    <a href="https://github.com/NoisyCake/vless_config_updater/blob/main/README.ru.md"><u><b>РУССКИЙ</b></u></a>
</p>

# vless_config_updater

Фоновый инструмент, который извлекает общедоступный список конфигураций Xray/Sing-box в виде URI и отфильтровывает только **рабочие** VLESS конфиги.
</div>

## Установка и настройка

> [!NOTE]
> Инструкция актуальна для Debian-based дистрибутивов Linux

Скачайте и установите необходимые инструменты:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install git

curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Клонируйте репозиторий и перейдите к нему:
```bash
git clone https://github.com/NoisyCake/vless_config_updater.git
cd vless_config_updater
cp .env.example .env
chmod +x set_timer.sh
```

### Переменные окружения
В файле `.env` содержится несколько переменных, которые нужно настроить:
|variable|description|example|
|:--:|:--|:--|
|STEAL_FROM|Исходный файл, который будет фильтроваться|https://raw.githubusercontent.com/Epodonios/v2ray-configs/refs/heads/main/Sub1.txt|
|CONFIG_FILE_URL|Результирующий файл, в который будут пушиться отфильтрованные конфиги|https://api.github.com/.../file.txt|
|GITHUB_TOKEN|Токен доступа GitHub (если файл находится в приватном репозитории)|ghp_dhoauigc7898374yduisdhSDHFHGf7|
|SPEED_LIMIT|Лимит фильтрации по скорости (целое число). Конфиги с меньшим результатом спидтеста не будут добавлены|5|
|CONFIGS_LIMIT|Определяет количество конфигов, при котором итоговый файл не будет запушен в удалённый репозиторий|1|
|UPDATE_DELAY|Определяет, как часто будет выполняться обновление конфигов в минутах (целое число)|60|
|LOG_RETENTION_DAYS|Определяет, сколько хранятся логи в днях (целое число)|7|

Чтобы подобрать оптимальное значение для <SPEED_LIMIT>, проведите несколько тестовых запусков со своего сервера, зайдите в логи (`nano logs/py.log`) и ищите строки "Server speed: ...". Возьмите подходящее число (например, среднее) и впишите его в переменную.  

---
## Запуск
Чтобы запустить фоновый процесс и создать файлы, отвечающие за его периодическую работу: `sudo ./set_timer.sh`. Эту же команду используйте, если внесли какие-то изменения в `.env`.

Теперь каждые <UPDATE_DELAY> минут программа будет выполняться и обновлять файл <CONFIG_URL_FILE>.

Чтобы проверить, сколько времени осталось до следующей итерации: `sudo systemctl status vless_config_updater.timer`. В строке "Trigger:" вы увидите оставшееся время.

---
## Лицензия

Проект распространяется под лицензией MIT. Подробности в файле `LICENSE`.

---
## Изменения и предложения

Предложения, сообщения об ошибках и pull requests приветствуются!
