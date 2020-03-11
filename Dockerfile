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

RUN python /usr/src/app/cash_flow/manage.py makemigrations
RUN python /usr/src/app/cash_flow/manage.py migrate

#ENTRYPOINT ["python", "/usr/src/app/cash_flow/manage.py", "runserver", "0.0.0.0:8000"]
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]