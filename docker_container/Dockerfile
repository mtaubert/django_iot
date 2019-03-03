FROM ubuntu:latest

RUN apt-get update
RUN apt-get -y upgrade

RUN apt-get install -y sqlite3 unzip
RUN apt install -y python3-pip python-setuptools

RUN mkdir /code
WORKDIR /code
RUN pip3 install django ttn geopy django-widget-tweaks validate_email
ADD . /code/
COPY ./django_iot-master.zip /code
RUN unzip django_iot-master.zip

EXPOSE 8000

# Run app.py when the container launches
CMD ["python3", "-u", "django_iot-master/manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["ls"]