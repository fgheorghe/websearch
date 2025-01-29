FROM ubuntu:latest

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip pipx 

COPY src /code

WORKDIR /code

RUN python3.10 -m venv venv
RUN . venv/bin/activate && pip install -r requirements.txt

 CMD . venv/bin/activate && streamlit run ui.py
