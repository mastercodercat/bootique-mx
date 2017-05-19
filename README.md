# Boutique Air MX Tracking System

## Deployment using fabric

Project has deployment setup to deploy using fabric and docker on staging/production server, so please follow these steps to configure deployment parameters.

- Put your SSH key pair (for connecting to server) into deploy/ssh/staging or deploy/ssh/production folder. Private key as `id_rsa`, public key as `id_rsa.pub`.
- Generate SSH key pair of remote server (for pulling from git) and link public key of the pair to any bitbucket account that can access the repo
- Copy `fabric_settings.py` from `fabric_settings.py.example` file and fill the parameters.
- Now you're ready to use `fab` command line tool to start deployment process.
- Deploy
    `fab staging bootstrap` - Only for the first time to setup environment
    `fab staging deploy` - Deploy latest code to server when using docker
    `fab staging deploynodocker` - Deploy latest code to server when not using docker
    * specify `staging` or `production` based on fabric settings
- To setup super user of django admin
  = open shell inside docker: `fab staging shell`
  = run the command `python manage.py createsuperuser`
- To test production environment on local, run these command:
    `docker-compose -f docker-compose.yml -f docker-compose-dev.yml build`
    `docker-compose -f docker-compose.yml -f docker-compose-dev.yml up -d`

## Local development

To run the application on local for development, please follow these steps.

Configure database connection

- In `[project folder]/mxtracking` directory, copy local_settings.py.example to local_settings.py
- Edit `DATABASES['default']` parameter to connection string of local database (postgres is used as default currently)

To run the project:

- Activate virtual environment
- Go to project root directory
- Run `python manage.py makemigrations inspection home routeplanning` to create migrations
- Run `python manage.py migrate` to migrate database
- Run `python manage.py runserver` to run project
- For building front end assets,
  = install node
  = Run `npm install` to install dependencies
  = Run `npm run watch` to watch and compile resource changes

Initial project configuration:

- Run `python manage.py createsuperuser` to create an admin
- Login to `http://localhost:8000/admin` to enter django admin
- Add Site model with site name `localhost`
- Add Social auth application as Google with api key and secret

Load fixures:

Run all the commands in the following order:
`python manage.py loaddata roles.json`
`python manage.py loaddata inspection.json`
`python manage.py loaddata aircraft.json`
`python manage.py loaddata aircraft_inspection_record.json`
`python manage.py loaddata airframes.json`
`python manage.py loaddata engines.json`
`python manage.py loaddata propellers.json`
`python manage.py loaddata lines.json`
`python manage.py loaddata lineparts.json`
`python manage.py loaddata tails.json`
`python manage.py loadflightcsv` (Before running this, put CSV file as `flights.csv` in routeplanning/fixtures/)
`python manage.py loadlinecsv` (Before running this, put `lines.csv` and `lineparts.csv` in routeplanning/fixtures/)

(Note that default CSV data is already in fixtures. Put CSV file into fixtures folder when you need to use new or updated data.)

Run test:

`python manage.py test`

* Note when SCSS file is modified, please restart django appserver.
