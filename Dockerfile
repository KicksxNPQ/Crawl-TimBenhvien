FROM python:3.11.1-buster

WORKDIR /app
COPY . .

RUN pip3 install -r requirements.txt

CMD scrapy runspider main.py