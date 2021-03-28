# docker  build -f Dockerfile -t tbot .
# docker run -ti --rm tbot


FROM python:3.8-alpine
RUN apk update && apk add py3-setuptools git && pip3 install requests

RUN addgroup -S app && adduser -S -G app app

WORKDIR /home/$USER
RUN git clone --single-branch -b main https://github.com/hjltu/tinkoff_client
WORKDIR tinkoff_client

ENTRYPOINT [ "python3", "test.py" ]

