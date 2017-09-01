#!/bin/bash
# start-server.sh

cd /code
cp ./mxtracking/docker_settings.py ./mxtracking/local_settings.py

# prepare uploads directory
mkdir ./static/uploads/

# clear bundles directory
cd ./static/bundles/
rm -f *
cd /code

# migration
python manage.py migrate

# fixtures
python manage.py loaddata roles.json
python manage.py loaddata inspection.json
python manage.py loaddata aircraft.json
python manage.py loaddata airframes.json
python manage.py loaddata engines.json
python manage.py loaddata propellers.json
python manage.py loaddata tails.json
python manage.py loaddata lines.json
python manage.py loaddata lineparts.json

# static assets
python manage.py collectstatic --noinput
NODE_ENV=production npm install
npm run build

# now boot
gunicorn mxtracking.wsgi:application -b 0.0.0.0:8000 -t 300 \
    --access-logfile /code/log/access.log \
    --error-logfile /code/log/error.log
