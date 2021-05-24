FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

RUN set -x && \
    apk --update --no-cache add \
        openssl-dev \
        libffi-dev \
        openldap-dev \
        zlib-dev \
        jpeg-dev \
        postgresql-client \
        postgresql-dev \
        build-base \
        gettext \
        git \
        py3-psutil \
        libxml2-dev \
        libxslt-dev \
        ca-certificates && \
    update-ca-certificates && \
    pip3 install --upgrade pip setuptools wheel
WORKDIR /www
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --ignore-installed -r requirements.txt

COPY . ./
