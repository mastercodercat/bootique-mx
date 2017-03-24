# Boutique Air MX Tracking System

Configure database connection

- In `[project folder]/mxtracking` directory, copy local_settings.py.example to local_settings.py
- Edit `DATABASES['default']` parameter to connection string of local database (postgres is used as default currently)

To run the project:

- Activate virtual environment
- Go to project root directory
- Run `python manage.py makemigrations inspection home` to create migrations
- Run `python manage.py migrate` to migrate database
- Run `python manage.py runserver` to run project

Initial project configuration:

- Run `python manage.py createsuperuser` to create an admin
- Login to `http://localhost:8000/admin` to enter django admin
- Add Site model with site name `localhost`
- Add Social auth application as Google with api key and secret

Load fixures:

Run all the commands in the following order:
`python manage.py loaddata inspection.json`
`python manage.py loaddata aircraft.json`
`python manage.py loaddata aircraft_inspection_record.json`
`python manage.py loaddata airframes.json`
`python manage.py loaddata engines.json`
`python manage.py loaddata propellers.json`

Run test:

`python manage.py test`

Recompile SCSS:

- Run `python manage.py compress` to build and compress SCSS files
- Restart django
