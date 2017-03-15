from django.conf.urls import url
from home import views

urlpatterns = [
    url(r'^aircraft/(?P<reg>[0-9a-zA-Z]+)/*$', views.aircraft_details, name='aircraft_details'),
    url(r'^aircraft/(?P<reg>[0-9a-zA-Z]+)/tasklist/*$', views.aircraft_task_list, name='aircraft_task_list'),
    url(r'^aircraft/(?P<reg>[0-9a-zA-Z]+)/mels/*$', views.aircraft_mels, name='aircraft_mels'),
    url(r'^$', views.overview, name='overview'),
]
