FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN python3 -m venv mltbenv

COPY requirements.txt .
RUN mltbenv/bin/pip install --no-cache-dir -r requirements.txt
RUN apt update -y && apt install android-sdk-libsparse-utils lz4 p7zip-full wget -y

CMD ["bash", "start.sh"]
