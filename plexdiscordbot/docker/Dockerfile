FROM python:3-alpine

WORKDIR /plexdiscordbot

RUN apk add --no-cache gcc musl-dev postgresql-dev bash

COPY ./docker/requirements.txt ./docker/
RUN pip install --no-cache-dir -r ./docker/requirements.txt

COPY . .

CMD ["./docker/wait-for-it.sh", "postgres:5432", "--", "python", "bot.py"]