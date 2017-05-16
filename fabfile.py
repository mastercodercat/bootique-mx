import os
from contextlib import contextmanager
from fabric.api import cd, env, prefix, run, sudo, task

from fabric_settings import *

env.hosts = []

@task
def staging():
    env.hosts = ['%s@%s' % (STAGING_SERVER_SSH_USER, STAGING_SERVER)]
    env.deploy_user = STAGING_SERVER_DEPLOY_USER
    env.key_filename = 'deploy/ssh/staging/id_rsa'
    if PASSWORD:
        env.password = PASSWORD


@task
def production():
    env.hosts = ['%s@%s' % (PRODUCTION_SERVER_SSH_USER, PRODUCTION_SERVER)]
    env.deploy_user = PRODUCTION_SERVER_DEPLOY_USER
    env.key_filename = 'deploy/ssh/production/id_rsa'
    if PASSWORD:
        env.password = PASSWORD


# Commands


@contextmanager
def source_virtualenv():  
    with prefix('source %s/bin/activate' % (VENV_ROOT)):
        yield


def clean():
    """Cleans Python bytecode"""
    sudo('find . -name \'*.py?\' -exec rm -rf {} \;')


def chown():
    """Sets proper permissions"""
    sudo('chown -R www-data:www-data %s' % PROJECT_ROOT)


def restart():
    sudo('systemctl restart uwsgi.service')


@task
def deploynodocker():
    """
    Deploys the latest tag to the production server
    """
    sudo('chown -R %s:%s %s' % (env.deploy_user, env.deploy_user, PROJECT_ROOT))

    with cd(PROJECT_ROOT):
        run('git pull origin master')
        with source_virtualenv():
            run('pip install -r %s/requirements.txt' % (PROJECT_ROOT))
            run('./manage.py collectstatic --noinput')
            run('./manage.py compress')
            run('./manage.py makemigrations inspection home routeplanning')
            run('./manage.py migrate')

    chown()
    restart()


@task
def deploy():
    """
    Deploys the latest tag to the production server using docker
    """
    with cd(PROJECT_ROOT):
        run('git pull origin master')
        run('docker-compose build')
        run('docker-compose up -d')


@task
def setupadmin():
    """
    Create django admin account
    """
    with cd(PROJECT_ROOT):
        run('docker-compose exec web bash')
        run('python manage.py createsuperuser')


@task
def bootstrap():
    """
    Setup server environment using docker
    """

    # Install docker
    sudo('apt-get update')
    sudo('apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')
    sudo("apt-add-repository 'deb https://apt.dockerproject.org/repo ubuntu-xenial main'")
    sudo('apt-get update')
    run('apt-cache policy docker-engine')
    sudo('apt-get install -y docker-engine')

    # Install docker-compose
    sudo('curl -L https://github.com/docker/compose/releases/download/1.13.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose')
    sudo('chmod +x /usr/local/bin/docker-compose')

    # Create Postgres data folder on host
    with cd('~'):
        run('mkdir postgres_data')
