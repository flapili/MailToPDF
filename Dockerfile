FROM ubuntu:22.04

RUN apt update && \
    apt install python3 python3-pip -y && \
    pip install playwright pydantic[email] croniter discord-webhook && \
    playwright install-deps && \
    playwright install chromium

VOLUME [ "/data" ]

COPY "main.py" .
ENTRYPOINT [ "python3", "-u", "main.py" ]