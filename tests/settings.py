DEBUG = True
SECRET_KEY = 'secret'

DATABASES = {
    'default': {
        'NAME': 'django_mcmo',
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = ['django_mcmo',
                  'django_nose']

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
