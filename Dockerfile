# pull official base image
FROM python:3.8.0-alpine

# set work directory
WORKDIR /usr/src/app
COPY . /usr/src/app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
# COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]