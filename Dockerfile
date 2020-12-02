FROM python:3.9-buster
LABEL maintainer="tinventory@jonathanweth.de"
LABEL org.label-schema.name="katharineum/tinventory"
LABEL org.label-schema.description="Inventory toolkit in order not to lose technology stuff anymore"
LABEL org.label-schema.vcs-url="https://github.com/Katharineum/tinventory"

ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
	libmariadbclient-dev yarnpkg gettext && \
	pip3 install --upgrade pip && \
	pip3 install uwsgi mysqlclient poetry && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /var/www/
COPY poetry.lock /var/www/
COPY pyproject.toml /var/www/
RUN poetry config virtualenvs.create false; poetry install;

COPY docker-setup/uwsgi-app.ini /etc/uwsgi/apps-enabled/uwsgi-app.ini
COPY docker-setup/init_and_run.sh /home/docker/init_and_run.sh

COPY web /var/www/
RUN mkdir -p /var/www/tmp/
RUN python3 manage.py yarn install
RUN python3 manage.py compilemessages

EXPOSE 3031
CMD ["/home/docker/init_and_run.sh"]
