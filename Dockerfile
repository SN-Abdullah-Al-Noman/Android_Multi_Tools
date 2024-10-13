FROM anasty17/mltb:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --break-system-packages
RUN apt install android-sdk-libsparse-utils
COPY . .

CMD ["bash", "start.sh"]
