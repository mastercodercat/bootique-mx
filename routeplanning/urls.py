from django.conf.urls import url

from routeplanning import views


urlpatterns = [
    url(r'^tail/add/*$', views.add_tail, name='add_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/*$', views.edit_tail, name='edit_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/delete/*$', views.delete_tail, name='delete_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/revision/(?P<revision_id>[0-9]+)/comingdue/*$', views.coming_due, name='coming_due'),

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
    url(r'^api/flight/getpage/*$', views.api_flight_get_page, name='api_flight_get_page'),
    url(r'^api/hobbs/(?P<hobbs_id>[0-9]+)/*$', views.api_get_hobbs, name='api_get_hobbs'),
    url(r'^api/hobbs/(?P<hobbs_id>[0-9]+)/remove/*$', views.api_delete_actual_hobbs, name='api_delete_actual_hobbs'),
    url(r'^api/revision/publish/*$', views.api_publish_revision, name='api_publish_revision'),
    url(r'^api/revision/clear/*$', views.api_clear_revision, name='api_clear_revision'),
    url(r'^api/revision/delete/*$', views.api_delete_revision, name='api_delete_revision'),

    url(r'^$', views.index, name='index'),
    url(r'^view-gantt/*$', views.view_gantt, name='view_gantt'),
]
