FROM python:3.8.5-alpine3.12
EXPOSE 3000
WORKDIR /work
COPY *.py omikuji_result.json requirements.txt /work/
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
