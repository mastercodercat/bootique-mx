from django.conf.urls import url

from routeplanning.views import api_views
from routeplanning.views import page_views


urlpatterns = [
    url(r'^tail/add/*$', page_views.add_tail, name='add_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/*$', page_views.edit_tail, name='edit_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/revision/(?P<revision_id>[0-9]+)/comingdue/*$', page_views.coming_due, name='coming_due'),

    url(r'^line/add/*$', page_views.add_line, name='add_line'),
    url(r'^line/(?P<line_id>[0-9]+)/*$', page_views.edit_line, name='edit_line'),
    
    url(r'^flights/*$', page_views.flights, name='flights'),
    url(r'^flights/add/*$', page_views.add_flight, name='add_flight'),
    url(r'^flights/(?P<flight_id>[0-9]+)/*$', page_views.edit_flight, name='edit_flight'),
    url(r'^flights/delete/*$', page_views.delete_flights, name='delete_flights'),

    url(r'^$', page_views.index, name='index'),
    url(r'^view-gantt/*$', page_views.view_current_published_gantt, name='view_current_published_gantt'),

    url(r'^api/loaddata/*$', api_views.api_load_data, name='api_load_data'),
    url(r'^api/line/(?P<line_id>[0-9]+)/delete/*$', api_views.delete_line, name='delete_line'),
    url(r'^api/tail/(?P<tail_id>[0-9]+)/delete/*$', api_views.delete_tail, name='delete_tail'),
    url(r'^api/tail/assignflight/*$', api_views.api_assign_flight, name='api_assign_flight'),
    url(r'^api/tail/assignstatus/*$', api_views.api_assign_status, name='api_assign_status'),
    url(r'^api/tail/hobbs/*$', api_views.api_save_hobbs, name='api_save_hobbs'),
    url(r'^api/tail/comingduelist/*$', api_views.api_coming_due_list, name='api_coming_due_list'),
    url(r'^api/assignment/move/*$', api_views.api_move_assignment, name='api_move_assignment'),
    url(r'^api/assignment/remove/*$', api_views.api_remove_assignment, name='api_remove_assignment'),
    url(r'^api/assignment/resize/*$', api_views.api_resize_assignment, name='api_resize_assignment'),
    url(r'^api/flight/uploadcsv/*$', api_views.api_upload_csv, name='api_upload_csv'),
    url(r'^api/flight/getpage/*$', api_views.api_flight_get_page, name='api_flight_get_page'),
    url(r'^api/hobbs/(?P<hobbs_id>[0-9]+)/*$', api_views.api_get_hobbs, name='api_get_hobbs'),
    url(r'^api/hobbs/(?P<hobbs_id>[0-9]+)/remove/*$', api_views.api_delete_actual_hobbs, name='api_delete_actual_hobbs'),
    url(r'^api/revision/publish/*$', api_views.api_publish_revision, name='api_publish_revision'),
    url(r'^api/revision/clear/*$', api_views.api_clear_revision, name='api_clear_revision'),
    url(r'^api/revision/delete/*$', api_views.api_delete_revision, name='api_delete_revision'),
]
