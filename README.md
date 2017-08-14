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
    `docker-compose -f docker-compose.yml -f docker-compose-local.yml build`
    `docker-compose -f docker-compose.yml -f docker-compose-local.yml up -d`

## Local development

To run the application on local for development, please follow these steps.

### Configure database connection

- In `[project folder]/mxtracking` directory, copy local_settings.py.example to local_settings.py
- Edit `DATABASES['default']` parameter to connection string of local database (postgres is used as default currently)

### Run the project

- Activate virtual environment
- Go to project root directory
- Run `pip install -r requirements/local.txt` to install local development dependencies (which includes test libraries in addition to main dependencies.)
- Run `python manage.py makemigrations inspection home routeplanning` to create migrations
- Run `python manage.py migrate` to migrate database
- Load fixtures (See below)
- Run `python manage.py runserver` to run project

### Build front end

- Install node
- Run `npm install` to install dependencies
- Run `npm run watch` to watch and compile resource changes

### Initial project configuration

- Run `python manage.py createsuperuser` to create an admin
- Login to `http://localhost:8000/admin` to enter django admin
- Add Site model with site name `localhost`
- Add Social auth application as Google with api key and secret
- You'll be likely seeing `Not enough permissions` when trying to access front end with created account. To fix this you need to set user role in `admin/User Profiles`.

### Load fixures

- Run this command to load fixtures: `./bin/load_all_data`
- After running this command, load flights CSV file in front end: Route Planning Gantt -> Flights page.

### Run test

- Run tests on back end:
    `npm run test:backend`
- Run tests on back end with coverage report:
    `npm run test:backend:coverage`
- Test front end Vue.js components:
    `npm run test:frontend`
