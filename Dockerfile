FROM python:3.11-slim-bullseye

RUN apt update && \
    apt install -y ffmpeg gettext && \
    useradd -u 1000 1000 && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /root/.ssh/

WORKDIR /Protocol
ADD . .
RUN mkdir -p ./Protocol/Data
RUN chmod +x ./build_locale.sh 
RUN ./build_locale.sh
RUN pip install -r requirements.txt

USER 1000

ENTRYPOINT ["python3", "__main__.py"]
