FROM python:3-alpine

WORKDIR /plexdiscordbot

COPY . .

RUN apk update \
&& apk add --no-cache gcc musl-dev postgresql-dev bash

RUN pip install --no-cache-dir -r ./docker/requirements.txt

CMD ["./docker/wait-for-it.sh", "postgres:5432", "--", "python", "bot.py"]