from django.conf.urls import url

from routeplanning.views import api_views
from routeplanning.views import page_views


urlpatterns = [
    url(r'^tail/add/*$', page_views.AddTailView.as_view(), name='add_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/*$', page_views.EditTailView.as_view(), name='edit_tail'),
    url(r'^tail/(?P<tail_id>[0-9]+)/revision/(?P<revision_id>[0-9]+)/comingdue/*$',
        page_views.ComingDueView.as_view(), name='coming_due'),

    url(r'^line/add/*$', page_views.AddLineView.as_view(), name='add_line'),
    url(r'^line/(?P<line_id>[0-9]+)/*$', page_views.EditLineView.as_view(), name='edit_line'),
    
    url(r'^flights/*$', page_views.flights, name='flights'),
    url(r'^flights/add/*$', page_views.add_flight, name='add_flight'),
    url(r'^flights/(?P<flight_id>[0-9]+)/*$', page_views.edit_flight, name='edit_flight'),
    url(r'^flights/delete/*$', page_views.delete_flights, name='delete_flights'),

    url(r'^$', page_views.IndexView.as_view(), name='index'),
    url(r'^view-gantt/*$', page_views.CurrentPublishedGanttView.as_view(), name='view_current_published_gantt'),

    url(r'^api/loaddata/*$', api_views.LoadDataView.as_view(), name='api_load_data'),
    url(r'^api/line/(?P<line_id>[0-9]+)/delete/*$', api_views.DeleteLineView.as_view(), name='delete_line'),
    url(r'^api/tail/(?P<tail_id>[0-9]+)/delete/*$', api_views.DeleteTailView.as_view(), name='delete_tail'),
    url(r'^api/tail/assignflight/*$', api_views.AssignFlightView.as_view(), name='api_assign_flight'),
    url(r'^api/tail/assignstatus/*$', api_views.AssignStatusView.as_view(), name='api_assign_status'),
    url(r'^api/tail/hobbs/*$', api_views.SaveHobbsView.as_view(), name='api_save_hobbs'),
    url(r'^api/tail/comingduelist/*$', api_views.ComingDueListView.as_view(), name='api_coming_due_list'),
    url(r'^api/assignment/move/*$', api_views.MoveAssignmentView.as_view(), name='api_move_assignment'),
    url(r'^api/assignment/remove/*$', api_views.RemoveAssignmentView.as_view(), name='api_remove_assignment'),
    url(r'^api/assignment/resize/*$', api_views.ResizeAssignmentView.as_view(), name='api_resize_assignment'),
    url(r'^api/flight/uploadcsv/*$', api_views.UploadCSVView.as_view(), name='api_upload_csv'),
    url(r'^api/flight/getpage/*$', api_views.FlightListView.as_view(), name='api_flight_get_page'),
    url(r'^api/hobbs/(?P<hobbs_id>[0-9]+)/*$', api_views.HobbsView.as_view(), name='api_hobbs'),
    url(r'^api/revision/publish/*$', api_views.PublishRevisionView.as_view(), name='api_publish_revision'),
    url(r'^api/revision/clear/*$', api_views.ClearRevisionView.as_view(), name='api_clear_revision'),
    url(r'^api/revision/delete/*$', api_views.DeleteRevisionView.as_view(), name='api_delete_revision'),
]
