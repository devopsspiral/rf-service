FROM python:3.8.1-alpine
# dev
# RUN pip install robotframework datetime requests flask flask-cors kubernetes
# RUN apk add --no-cache \
#     build-base \
#     libffi-dev \
#     && pip install gevent \
#     && apk del build-base
# RUN pip install --index-url https://test.pypi.org/simple/ rf-service==0.3.6

#release
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    && pip install gevent \
    && apk del build-base \
    && pip install rf-service==0.3.1

CMD rf-service