FROM python:3-alpine

WORKDIR /plexdiscordbot

RUN apk add gcc musl-dev

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "./bot.py"]