#!/bin/sh
python /usr/src/app/cash_flow/manage.py makemigrations
python /usr/src/app/cash_flow/manage.py migrate
python /usr/src/app/cash_flow/manage.py runserver 0.0.0.0:80