# Boutique Air MX Tracking System

Configure database connection

- In `[project folder]/mxtracking` directory, copy local_settings.py.example to local_settings.py
- Edit `DATABASES['default']` parameter to connection string of local database (postgres is used as default currently)

To run the project:

- Activate virtual environment
- Go to project root directory
- Run `python manage.py makemigrations` to create migrations
- Run `python manage.py migrate` to migrate database
- Run `python manage.py runserver` to run project

Initial project configuration:

- Run `python manage.py createsuperuser` to create an admin
- Login to `http://localhost:8000/admin` to enter django admin
- Add Site model with site name `localhost`
- Add Social auth application as Google with api key and secret

Load fixures:

Run all the commands:
`python manage.py aircrafts.json`
`python manage.py airframes.json`
`python manage.py engines.json`
`python manage.py propellers.json`