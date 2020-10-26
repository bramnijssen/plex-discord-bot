FROM python:3-alpine as base

WORKDIR /plexdiscordbot

COPY ./requirements.txt ./requirements.txt

RUN apk update \
&& apk add --no-cache gcc musl-dev

RUN pip install --no-cache-dir -r ./requirements.txt

COPY ./src .

# IMAGE: DEBUGGER
FROM base as debug

RUN pip install --no-cache-dir debugpy

CMD ["python", "-m", "debugpy", "--listen", "0.0.0.0:5678", "bot.py"]

# IMAGE: PRODUCTION
FROM base as prod

CMD ["python", "bot.py"]