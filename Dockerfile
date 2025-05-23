FROM python:3.13.3-slim

WORKDIR /app

COPY ./updater ./updater

RUN apt-get update && apt-get install curl tar -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r /app/updater/requirements.txt && \
    curl -L -o sing-box.tar.gz https://github.com/SagerNet/sing-box/releases/download/v1.11.11/sing-box-1.11.11-linux-amd64.tar.gz && \
    mkdir -p tmp logs && \
    tar -xzf sing-box.tar.gz -C tmp && \
    cp tmp/sing-box-1.11.11-linux-amd64/sing-box /app && \
    rm -rf tmp sing-box.tar.gz install.sh
    
CMD ["python", "updater/main.py"]
