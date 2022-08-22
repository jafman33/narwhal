# syntax=docker/dockerfile:1

FROM python:3.8.9
WORKDIR /narwhal-docker
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY . .
CMD [ "python", "-m" , "flask", "run"]