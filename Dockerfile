FROM python:3.9

RUN apt-get update && apt-get install -y vim

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY apps /srv/apps

WORKDIR /srv

EXPOSE 8425

ENV DB_NAME ''
ENV DB_USER ''
ENV DB_HOST ''
ENV DB_PASSWORD ''

CMD ["python", "-m", "apps.index"]
COPY alembic /srv/alembic
COPY alembic.ini /srv/alembic.ini
COPY scripts /srv/scripts
RUN pip install gunicorn==20.0.4

