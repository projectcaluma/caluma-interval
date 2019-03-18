FROM python:3.6.8-alpine3.9@sha256:c3b0a0317d0759a0c0b8cf2b2c60ea09729bc9b7faf464ee67434f45de2bb3d1

ARG requirements=requirements.txt

RUN apk add --no-cache postgresql-libs bash && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    wget -q https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -P /usr/local/bin && \
    chmod +x /usr/local/bin/wait-for-it.sh

WORKDIR /app

COPY requirements.txt requirements-dev.txt /app/
RUN pip install --no-cache-dir -r ${requirements} && \
    apk --purge del .build-deps
COPY . /app

CMD /bin/sh -c "wait-for-it.sh ${DATABASE_HOST:-db}:${DATABASE_PORT:-5432} -- wait-for-it.sh ${CALUMA_HOST:-caluma}:${CALUMA_PORT:-8000} -- python -m caluma_interval"
