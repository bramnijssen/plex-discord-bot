FROM python:3

WORKDIR /plexdiscordbot

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "./bot.py"]