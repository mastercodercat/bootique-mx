from django.conf.urls import url

from routeplanning import views


urlpatterns = [
    url(r'^tail/add/*$', views.add_tail, name='add_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/*$', views.edit_tail, name='edit_tail'),
    url(r'^line/add/*$', views.add_line, name='add_line'),
    url(r'^line/(?P<line_id>[0-9]+)/*$', views.edit_line, name='edit_line'),
    url(r'^flights/*$', views.flights, name='flights'),
    url(r'^flights/add/*$', views.add_flight, name='add_flight'),

    url(r'^api/loaddata/*$', views.api_load_data, name='api_load_data'),
    url(r'^api/assignflight/*$', views.api_assign_flight, name='api_assign_flight'),

    url(r'^$', views.index, name='index'),
]
