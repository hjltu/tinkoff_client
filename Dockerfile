# docker  build --force-rm -f Dockerfile -t tbot .
# docker run -ti --rm tbot


FROM python:3.8-alpine
LABEL maintainer="hjltu@ya.ru"

RUN apk update && apk add py3-setuptools git && pip3 install requests

ENV USER=tbot
RUN addgroup -S $USER && adduser -S -G $USER $USER
USER $USER

WORKDIR /home/$USER
RUN git clone --single-branch -b main https://github.com/hjltu/tinkoff_client
WORKDIR tinkoff_client

ENTRYPOINT [ "python3", "test.py" ]

