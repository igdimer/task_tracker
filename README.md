# Task Tracker

[![Tests](https://github.com/igdimer/task_tracker/actions/workflows/main.yml/badge.svg)](https://github.com/igdimer/task_tracker/actions/workflows/main.yml)

This project is a prototype of task tracker. Functionality ideas were taken from Jira.

**Stack**:

- Python 3.11
- Django 4.2
- Django Rest Framework 3.14
- PostgreSQL
- Docker
- Celery

Also pytest, isort, flake8, mypy are used for adjusting and testing code.

Approach to building project structure is partly based on [HackSoftware/Django Styleguide](https://github.com/HackSoftware/Django-Styleguide).

### Summary of entities and resources

- Users
- Projects
- Releases
- Issues
- Comments

Authentication system is based on JWT tokens. Admin-user can create users.

Use command ```python manage.py createadmin``` to create admin-user. This command is not associated with django command ```python manage.py createsuperuser```.
To access on django-admin site use the last one.

Users can create, edit and get projects, releases, issues and comments.
Projects have releases. Issues should belong to project and can be connected to release. Comments can be added to issue.

### Launch project

To launch project locally clone repository and run ```docker-compose up``` in the project directory.

After that openapi documentation is available on http://0.0.0.0:8000/docs
