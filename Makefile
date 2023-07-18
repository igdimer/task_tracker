run_app:
	python manage.py runserver 0.0.0.0:8000

update_requirements:
	pip-compile && pip-compile requirements.dev.in

upgrade_requirements:
	pip-compile --upgrade && pip-compile requirements.dev.in --upgrade

sync_requirements:
	pip-sync requirements.txt requirements.dev.txt

check:
	isort server manage.py
	flake8 server manage.py
	mypy server manage.py
	pytest server
	python manage.py check --fail-level=WARNING
	yamllint --strict .
