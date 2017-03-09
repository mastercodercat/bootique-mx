from django.conf.urls import url
from home import views

urlpatterns = [
    url(r'^aircraft/(?P<aircraft>[0-9a-zA-Z]+)/*$', views.aircraft_details, name='aircraft_details'),
    url(r'^$', views.overview, name='overview'),
]
