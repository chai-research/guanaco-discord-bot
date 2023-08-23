FROM selenium/standalone-chrome


USER root
RUN apt update
RUN apt-get install -y python3-pip

COPY . /app
WORKDIR ./app

RUN python3 -m pip install -r requirements.txt

CMD python3 bot.py