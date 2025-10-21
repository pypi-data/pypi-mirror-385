ARG PYVERSION=py39
FROM baseten/baseten-server-gpu-base-$PYVERSION:latest

COPY ./src/server_requirements.txt server_requirements.txt
RUN pip install -r server_requirements.txt

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

# BaseTen specific build arguments and environment variables
ARG RUNTIME_ENV
ARG SENTRY_URL
ENV RUNTIME_ENV=$RUNTIME_ENV
ENV SENTRY_URL=$SENTRY_URL

ARG MODEL_CLASS
ARG MODEL_CLASS_DEFINITION_FILE

ENV PORT 8080

ENV APP_HOME /app
WORKDIR $APP_HOME
ENV MODEL_CLASS_NAME=$MODEL_CLASS
ENV MODEL_CLASS_FILE=$MODEL_CLASS_DEFINITION_FILE
COPY ./src .
COPY ./config.yaml config.yaml

RUN if [ -f "/usr/local/lib/python3.9/site-packages/table_logger/table_logger.py" ]; then \
 sed -i '80d;86d' /usr/local/lib/python3.9/site-packages/table_logger/table_logger.py; \
fi

CMD exec python3 inference_server.py
