from django.urls import path
from . import views

urlpatterns = [
    # Single record
    path('',                views.AttendanceListCreateView.as_view(),  name='attendance_list'),
    path('<int:pk>/',       views.AttendanceDetailView.as_view(),      name='attendance_detail'),

    # Bulk mark
    path('bulk-mark/',      views.BulkMarkAttendanceView.as_view(),    name='bulk_mark'),

    # Sessions
    path('sessions/',       views.AttendanceSessionListView.as_view(), name='session_list'),
    path('sessions/<int:session_id>/finalize/',
                            views.FinalizeSessionView.as_view(),       name='finalize_session'),
]