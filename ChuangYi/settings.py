# encoding: utf-8
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = ['*']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$j&$n^69qfra)^wm!asqi*+y6qef3gbcxq-efut$5g*+^1s340'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Application definition
WSGI_APPLICATION = 'ChuangYi.wsgi.application'
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'admin.apps.ChuangYiAdmin',
    'main.apps.ChuangYi',
    'modellib.apps.ModellibConfig',
    'web.apps.WebConfig',
    'django_crontab',
]

CRONJOBS = [
    ('00 00 * * *', 'django.core.management.call_command', ['build_models'], {},
     '>> /var/log/run.log'),
]

ROOT_URLCONF = 'ChuangYi.urls'
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
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'test.db'),
    },
}
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ChuangYiTest',   # 数据库名称
        'USER': 'root',       # 数据库用户名
        'PASSWORD': 'cyadmin',   # 数据库密码
        'HOST': 'localhost',  # 数据库主机，留空默认为localhost
        'PORT': '3306',       # 数据库端口
    }
}

# Internationalization
LANGUAGE_CODE = 'zh-cn'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = False
USE_L10N = False
USE_TZ = False

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

# Server info
SERVER_URL = 'http://chuangyh.com:8000/'
DEFAULT_ICON_URL = 'http://chuangyh.com:8000/uploaded/default_icon.jpg'

# Recommender arguments
USER_TAG_SCORE = 100                # 用户标签的特征模型贡献度
USER_TEAM_TAG_SCORE = 10            # 用户所在团队标签的特征模型贡献度
USER_FOLLOWED_TAG_SCORE = 2         # 用户关注对象标签的特征模型贡献度

USER_VIEW_SCORE = 1                 # 用户浏览对象标签的特征模型贡献度
USER_LIKE_SCORE = 5                 # 用户点赞对象标签的特征模型贡献度

USER_BEHAVIOR_ANALYSIS_CIRCLE = 7   # 用户模型可变部分行为分析周期（天）

TEAM_TAG_SCORE = 100                # 团队标签的特征模型贡献度
TEAM_MEMBER_TAG_SCORE = 2           # 团队成员标签的特征模型贡献度
