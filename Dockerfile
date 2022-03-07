FROM python:3.10.2-alpine3.15
WORKDIR /work
COPY omikuji_result.json requirements.txt ./
COPY slackbot/ slackbot/
RUN pip install -U pip && pip install -r requirements.txt
ENTRYPOINT ["python", "-m", "slackbot"]
