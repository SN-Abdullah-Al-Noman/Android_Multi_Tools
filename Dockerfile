FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN apt update -y && apt install android-sdk-libsparse-utils lz4 p7zip-full wget -y
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages
COPY . .

CMD ["bash", "start.sh"]
