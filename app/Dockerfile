FROM python:3.8

ENV PYTHONIOENCODING utf-8

WORKDIR /opt/app

COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt