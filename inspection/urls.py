from django.conf.urls import url

from inspection import views


urlpatterns = [
    url(r'^create/*$', views.create_inspection_program, name='create_inspection_program'),
    url(r'^(?P<program_id>[0-9a-zA-Z]+)/*$', views.inspection_program_details, name='inspection_program_details'),
    url(r'^(?P<program_id>[0-9a-zA-Z]+)/task/add/*$', views.add_inspection_task, name='add_inspection_task'),
    url(r'^$', views.index, name='index'),
]
