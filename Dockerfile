FROM python:3.10.2-alpine3.15
EXPOSE 3000
WORKDIR /work
COPY *.py omikuji_result.json requirements.txt /work/
COPY modules/ modules/
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
