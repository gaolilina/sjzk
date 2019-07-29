from django.conf.urls import url, include

from admin import urls as admin_url
from web import urls as web_url
from main import urls as app_url
from cms import urls as cms_url

urlpatterns = [
    # 这两个是导入其他工程
    url(r'^admin/', include(admin_url, namespace='admin')),
    url(r'^web/', include(web_url, namespace='web')),
    url(r'^cms/', include(cms_url)),
    url(r'^app/', include(app_url)),
]
