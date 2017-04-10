from django.conf.urls import url

from common import views


urlpatterns = [
    url(r'^$', views.index_redirect, name='index_redirect'),
]
