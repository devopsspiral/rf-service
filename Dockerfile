FROM python:3.8.1-alpine

RUN pip install rf-service==0.1.0

CMD rf-service