import os
from contextlib import contextmanager
from fabric.api import cd, env, prefix, run, sudo, task

from fabric_settings import *

env.hosts = []

@task
def staging():
    env.hosts = ['%s@%s' % (STAGING_SERVER_SSH_USER, STAGING_SERVER)]
    env.environment = 'production'
    env.deploy_user = STAGING_SERVER_DEPLOY_USER
    env.key_filename = 'fabric/ssh/id_rsa'


@task
def production():
    env.hosts = ['%s@%s' % (PRODUCTION_SERVER_SSH_USER, PRODUCTION_SERVER)]
    env.environment = 'production'
    env.deploy_user = PRODUCTION_SERVER_DEPLOY_USER


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
def deploy():
    """
    Deploys the latest tag to the production server
    """
    sudo('chown -R %s:%s %s' % (env.deploy_user, env.deploy_user, PROJECT_ROOT))

    with cd(PROJECT_ROOT):
        prev_password = env.password
        sudo('git pull origin master', user=env.deploy_user)
        env.password = GIT_PASSWORD
        with source_virtualenv():
            run('pip install -r %s/requirements.txt' % (PROJECT_ROOT))
            run('./manage.py collectstatic --noinput')
            run('./manage.py compress')
            run('./manage.py makemigrations inspection home routeplanning')
            run('./manage.py migrate')

    chown()
    restart()


@task
def bootstrap():
    """Bootstrap the latest code at the app servers"""
    # Not implemented yet
    pass
