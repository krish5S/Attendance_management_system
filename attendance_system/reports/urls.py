from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/',                          views.DashboardSummaryView.as_view(),        name='dashboard'),
    path('daily/',                              views.DailyAttendanceReportView.as_view(),   name='daily_report'),
    path('monthly/',                            views.MonthlyAttendanceReportView.as_view(), name='monthly_report'),
    path('low-attendance/',                     views.LowAttendanceAlertView.as_view(),      name='low_attendance'),
    path('student/<int:student_id>/',           views.StudentAttendanceReportView.as_view(), name='student_report'),
    path('class/<int:class_id>/',               views.ClassAttendanceReportView.as_view(),   name='class_report'),
]