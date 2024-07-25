# This Dockerfile is part of the Dockerfile troubleshooting exercise

FROM ubuntu:20.04
RUN sudo apt-get install python3
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
CMD "python3 app.py"
