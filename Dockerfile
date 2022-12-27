FROM python:3.11

WORKDIR /home

ENV TELEGRAM_API_TOKEN='5940851528:AAGtL-O8ob4yLp6qimyKMT4T1UNUOgNXQIg'
ENV TELEGRAM_ACCESS_ID=['217096899','226098376']

ENV TZ=Europe/Kyiv
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip aiogram pytz && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "server.py"]

