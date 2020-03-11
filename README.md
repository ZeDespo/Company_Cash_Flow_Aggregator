# Django Example Project

This repository is a sample API that goes onto the SEC website and pulls a company's Consolidated Statements of 
Cash Flows, parses it, and commits the changes to the database. This repository demonstrates:
- Basic understanding of Django (request handling, ORM, and project structure).
- Web scraping.
- Well-documented and unit tested code. 

### How to use

- Install pipenv: `pip3 install pipenv`
- Open a terminal and navigate to the first "cash_flows" directory. 
- Perform the following commands to launch and configure the virtual environment and create the database for the 
project: 
```
pipenv shell
pipenv lock
pipenv sync
python cash_flows/manage.py makemigrations
python cash_flows/manage.py migrate
```
- Run the server by using: `python cash_flows/manage.py runserver`
- Make calls to the API (http://localhost:8000) to test the functionality
    - Please read the docstrings for each view to understand input and output for each endpoint. 
- [Optional] if you would like to test the project within Django, you can do so by running
 `python cash_flows/manage.py test cscf`