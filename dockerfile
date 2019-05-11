FROM python:3.6

ADD requirements.txt /app/requirements.txt
WORKDIR /app/
RUN pip install -r requirements.txt

ENV SETTINGS /app/settings.yaml
ENV GITHUB_PRIVATE_KEY /app/github_app.private-key.pem

ADD ./gitconsensusservice/ /app/gitconsensusservice

RUN useradd -ms /bin/bash gitconsensusservice
USER gitconsensusservice

ADD ./docker/start_worker.sh /home/gitconsensusservice/start_worker.sh

ENTRYPOINT /home/gitconsensusservice/start_worker.sh