FROM ubuntu:22.04

COPY . PhysMode

RUN apt-get update \
    && apt-get -y install --no-install-recommends python3 \
    && apt-get -y install --no-install-recommends python3-django \
    && apt-get -y install --no-install-recommends python3-pip \
    && cd PhysMode && pip3 install -r requirements.txt
