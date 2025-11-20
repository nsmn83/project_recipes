FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./requirements.txt .

EXPOSE 5000

ENV FLASK_RUN_HOST=0.0.0.0

ENV FLASK_APP=app.py

ENV FLASK_DEBUG=1

CMD ["flask", "run"]
