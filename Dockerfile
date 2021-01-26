FROM python:3.9

RUN apt-get update && apt-get install -y vim

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY /apps /apps

WORKDIR /apps

EXPOSE 8425

ENV MAPBOX_ACCESS_TOKEN pk.eyJ1IjoidGFuanVua2Fpc3BkaWdpdGFsIiwiYSI6ImNrOHBqODR0bzFrcm4zZ3FveGgwdjBpeDQifQ.TtZsio5IHPT7b1TCpvCJyQ

CMD ["python", "-m", "index"]
