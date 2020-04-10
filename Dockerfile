FROM python:3.8.1-alpine
# dev
# RUN pip install robotframework datetime requests flask flask-cors
# RUN apk add --no-cache \
#     build-base \
#     && pip install gevent \
#     && apk del build-base
# RUN pip install --index-url https://test.pypi.org/simple/ rf-service==0.x.0 

#release
RUN apk add --no-cache \
    build-base \
    && pip install gevent \
    && apk del build-base \
    && pip install rf-service==0.2.0

CMD rf-service