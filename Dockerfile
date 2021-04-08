FROM python:3.9.2-alpine3.13
# dev
# RUN pip install --upgrade pip \
#     && pip install robotframework datetime requests flask flask-cors kubernetes
# RUN apk add --no-cache --virtual build-dependencies \
#     build-base \
#     libffi-dev \
#     musl-dev \
#     python3-dev \
#     openssl-dev \
#     cargo \
#     && pip install azure-storage-blob gevent\
#     && apk del build-dependencies
# RUN pip install --index-url https://test.pypi.org/simple/ rf-service==0.3.8

#release
RUN apk add --no-cache --virtual build-dependencies \
    build-base \
    libffi-dev \
    musl-dev \
    python3-dev \
    openssl-dev \
    cargo \
    && pip install gevent rf-service==0.3.2\
    && apk del build-dependencies

CMD rf-service