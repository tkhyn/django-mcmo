import os

DEBUG = True
SECRET_KEY = 'secret'

ROOT_URLCONF = 'tests.urls'

STATIC_URL = '/static/'
MEDIA_URL = '/media/'


DATABASES = {
    'default': {
        'NAME': 'django_mcmo',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = ('tests',
                  'django_nose')

MIDDLEWARE_CLASSES = ()

TEMPLATE_DIRS = os.path.join(os.path.dirname('__file__'), 'templates')

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
