# Task Tracker

This project is a prototype of task tracker. Functionality ideas were taken from Jira.

**Stack**:

- Python 3.11
- Django 4.2
- Django Rest Framework 3.14
- PostgreSQL
- Docker

Also pytest, isort, flake8, mypy were used for adjusting and testing code.

Approach to building project structure is partly based on [HackSoftware/Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

### Summary of entities and resources

- Users
- Projects
- Releases
- Issues
- Comments

Authentication system is based on JWT tokens. Registration by email and password, then get access and refresh tokens.

Users can create, edit and get projects, releases, issues and comments.
Projects have releases. Issues should belong to project and can be connected to release. Comments can be added to issue.

### Launch project

To launch project locally clone repository and run ```docker-compose up``` in the project directory.
