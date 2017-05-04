from django.conf.urls import url

from routeplanning import views


urlpatterns = [
    url(r'^tail/add/*$', views.add_tail, name='add_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/*$', views.edit_tail, name='edit_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/delete/*$', views.delete_tail, name='delete_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/comingdue/*$', views.coming_due, name='coming_due'),

    url(r'^line/add/*$', views.add_line, name='add_line'),
    url(r'^line/(?P<line_id>[0-9]+)/*$', views.edit_line, name='edit_line'),
    url(r'^line/(?P<line_id>[0-9]+)/delete/*$', views.delete_line, name='delete_line'),

    url(r'^flights/*$', views.flights, name='flights'),
    url(r'^flights/add/*$', views.add_flight, name='add_flight'),
    url(r'^flights/(?P<flight_id>[0-9]+)/*$', views.edit_flight, name='edit_flight'),
    url(r'^flights/delete/*$', views.delete_flights, name='delete_flights'),

    url(r'^api/loaddata/*$', views.api_load_data, name='api_load_data'),
    url(r'^api/tail/assignflight/*$', views.api_assign_flight, name='api_assign_flight'),
    url(r'^api/tail/assignstatus/*$', views.api_assign_status, name='api_assign_status'),
    url(r'^api/tail/hobbs/*$', views.api_save_hobbs, name='api_save_hobbs'),
    url(r'^api/tail/comingduelist/*$', views.api_coming_due_list, name='api_coming_due_list'),
    url(r'^api/assignment/move/*$', views.api_move_assignment, name='api_move_assignment'),
    url(r'^api/assignment/remove/*$', views.api_remove_assignment, name='api_remove_assignment'),
    url(r'^api/assignment/resize/*$', views.api_resize_assignment, name='api_resize_assignment'),
    url(r'^api/flight/uploadcsv/*$', views.api_upload_csv, name='api_upload_csv'),

    url(r'^$', views.index, name='index'),
]
