from django.conf.urls import url

from ..views.system import *

urls = [
    url(r'^version_number/$', VersionNumber.as_view(), name='version_number'),
]