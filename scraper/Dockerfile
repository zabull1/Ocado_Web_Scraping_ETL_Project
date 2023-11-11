FROM python:3.8

ENV PYTHONUNBUFFERED 1
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /scraper

COPY ./scraper /scraper

WORKDIR /scraper