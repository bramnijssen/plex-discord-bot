FROM python:3-alpine

WORKDIR /plexdiscordbot

RUN apk add --no-cache gcc musl-dev

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "./bot.py"]