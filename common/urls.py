from django.conf.urls import url

from common.views import page_views


urlpatterns = [
    url(r'^$', page_views.index_redirect, name='index_redirect'),
]
