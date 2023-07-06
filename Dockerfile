FROM python:3.10-slim-bullseye

RUN apt update && \
    apt install -y ffmpeg && \
    useradd -u 1000 1000 && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /root/.ssh/

WORKDIR /Protocol
ADD . .
RUN mkdir -p ./Protocol/Data
 
RUN pip install -r requirements.txt

USER 1000

ENTRYPOINT ["python3", "__main__.py"]
