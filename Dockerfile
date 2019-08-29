FROM python:3.6.8-alpine3.9@sha256:d1c2369c7ac9cadca46c94678a5bf589ab09c3b737fa37ed4b3b448da16491ad

ARG requirements=requirements.txt
WORKDIR /app
COPY requirements.txt requirements-dev.txt /app/

RUN apk add --no-cache bash && \
    wget -q https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -P /usr/local/bin && \
    chmod +x /usr/local/bin/wait-for-it.sh && \
    if [ "$requirements" = "requirements-dev.txt" ]; then apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev; fi && \
    pip install --no-cache-dir -r ${requirements} && \
    if [ "$requirements" = "requirements-dev.txt" ]; then apk --purge del .build-deps; fi

COPY . /app

CMD /bin/sh -c "wait-for-it.sh ${CALUMA_HOST:-caluma}:${CALUMA_PORT:-8000} -- python -m caluma_interval"
