# Django Example Project

This repository is a sample API that goes onto the SEC website and pulls a company's Consolidated Statements of 
Cash Flows, parses it, and commits the changes to the database. This repository demonstrates:
- Basic understanding of Django (request handling, ORM, and project structure).
- Web scraping.
- Well-documented and unit tested code. 

### How to use

It's as simple as running `docker build -t django_app .` and then running `docker run -p 8000:8000 django_app`.
The name "django_app" can be replaced with whatever name you so choose. 