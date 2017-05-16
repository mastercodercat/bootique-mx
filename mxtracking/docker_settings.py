DEBUG = False   # Should be False for production server

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

ALLOWED_HOSTS = ['*']    # Allowed Hosts config on Production server

# COMPRESS_OFFLINE = False       # Uncomment this line for development. Sets Django compressor to compress on the fly.
