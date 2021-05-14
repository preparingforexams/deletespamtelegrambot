FROM python:3.8-slim

WORKDIR /usr/src/app

ADD main.py .
ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD python -B -OO main.py
