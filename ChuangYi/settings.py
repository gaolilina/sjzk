import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$j&$n^69qfra)^wm!asqi*+y6qef3gbcxq-efut$5g*+^1s340'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition
WSGI_APPLICATION = 'ChuangYi.wsgi.application'
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'admin.apps.ChuangYiAdmin',
    'main.apps.ChuangYi'
]
ROOT_URLCONF = 'main.urls'
MIDDLEWARE_CLASSES = ['main.utils.abort.AbortExceptionHandler']
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test.db'),
    },
}

# Internationalization
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = False
USE_L10N = False
USE_TZ = True

DATETIME_FORMAT = 'Y-m-d H:i:s'
DATETIME_INPUT_FORMAT = ['%Y-%m-%d %H:%M:%S']
DATE_FORMAT = 'Y-m-d'
DATE_INPUT_FORMAT = ['%Y-%m-%d']


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = (   
  os.path.join(BASE_DIR, 'static'), 
)


# Uploaded files
UPLOADED_URL = '/uploaded/'
UPLOADED_ROOT = os.path.join(BASE_DIR, 'uploaded')
