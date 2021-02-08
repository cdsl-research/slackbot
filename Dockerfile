FROM python:3.8.5-alpine3.12
EXPOSE 3000
WORKDIR /work
COPY app.py requirements.txt tokenizer.py /work/
RUN pip install -r requirements.txt
CMD ["python", "app.py"]