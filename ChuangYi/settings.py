# ChuangYi Project Settings
# https://docs.djangoproject.com/en/1.9/topics/settings/
# https://docs.djangoproject.com/en/1.9/ref/settings/

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-j&$n^69qfra)^wm!asqi*+y6qef3gbcxq-efut$5g*+^1s340'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    # 'django.contrib.staticfiles',

    # 'admin.apps.AdminConfig',
    'user.apps.UserConfig',
    'team.apps.TeamConfig',
    'activity.apps.ActivityConfig',

    'comment.apps.CommentConfig',
    # 'event.apps.EventConfig',
    'invitation.apps.InvitationConfig',
    'location.apps.LocationConfig',
    'message.apps.MessageConfig',
    'need.apps.NeedConfig',
    # 'notification.apps.NotificationConfig',
    'profiles.apps.ProfilesConfig',
    'tag.apps.TagConfig',
    'task.apps.TaskConfig',

    'bookmark.apps.BookmarkConfig',
    'follow.apps.FollowConfig',
    'friend.apps.FriendConfig',
    'like.apps.LikeConfig',
    'visit.apps.VisitConfig'
]

MIDDLEWARE_CLASSES = [
    # 'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    # 'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ChuangYi.urls'

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

WSGI_APPLICATION = 'ChuangYi.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ChuangYi',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '192.168.189.128',
        'PORT': '5432',
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = False
USE_L10N = False
USE_TZ = False

DATETIME_FORMAT = 'Y-m-d H:i:s'
DATE_FORMAT = 'Y-m-d'
TIME_FORMAT = 'H:i:s'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/upload/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'upload')
