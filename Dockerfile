FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Dependencies and scripts setup
RUN apk add --update --no-cache postgresql-client curl
RUN apk add --update --no-cache --virtual .tmp-build-deps \
  gcc  libc-dev linux-headers postgresql-dev python3-dev 

COPY Pipfile .
COPY Pipfile.lock .
RUN pip install pipenv==2018.11.26 && \
  pipenv install --system

RUN apk del .tmp-build-deps

RUN adduser -D user

# Add code and directories
RUN mkdir /off_by_one
WORKDIR /off_by_one/
COPY ./django /off_by_one/django

WORKDIR /off_by_one/django
USER user