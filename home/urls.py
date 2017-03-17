from django.conf.urls import url
from home import views

urlpatterns = [
    url(r'^(?P<reg>[0-9a-zA-Z]+)/*$', views.aircraft_details, name='aircraft_details'),
    url(r'^(?P<reg>[0-9a-zA-Z]+)/tasklist/*$', views.aircraft_task_list, name='aircraft_task_list'),
    url(r'^(?P<reg>[0-9a-zA-Z]+)/mels/*$', views.aircraft_mels, name='aircraft_mels'),
    url(r'^(?P<reg>[0-9a-zA-Z]+)/assign/*$', views.aircraft_assign_program, name='aircraft_assign'),
    url(r'^$', views.overview, name='overview'),
]
