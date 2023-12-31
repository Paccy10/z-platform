FROM python:3.10.2-slim-bullseye

ENV APP_HOME=/app
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

LABEL description="Development image for ZPlatform API"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y libpq-dev \ 
    && apt-get install -y gettext \ 
    && apt-get install -y netcat gcc postgresql \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/* 

RUN pip3 install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY ./docker/development/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./docker/development/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

COPY ./docker/development/django/worker /worker
RUN sed -i 's/\r$//g' /worker
RUN chmod +x /worker

ENTRYPOINT [ "/entrypoint" ]