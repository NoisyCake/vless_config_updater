FROM python:3.13.3-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install curl tar -y && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r updater/requirements.txt && \
    curl -L -o sing-box.tar.gz https://github.com/SagerNet/sing-box/releases/download/v1.11.11/sing-box-1.11.11-linux-amd64.tar.gz
RUN mkdir -p tmp && \
    tar -xzf sing-box.tar.gz -C tmp && \
    cp tmp/sing-box-1.11.11-linux-amd64/sing-box /app && \
    rm -rf tmp sing-box.tar.gz
    
CMD ["python", "updater/main.py"]
