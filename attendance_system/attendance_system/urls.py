from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

# Admin branding
admin.site.site_header = "Attendance Management System"
admin.site.site_title  = "AMS Admin Portal"
admin.site.index_title = "Welcome to AMS Admin"

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('ui/login/', TemplateView.as_view(template_name='ui/login.html'), name='ui_login'),
    path('ui/register/', TemplateView.as_view(template_name='ui/register.html'), name='ui_register'),
    path('ui/dashboard/', TemplateView.as_view(template_name='ui/dashboard.html'), name='ui_dashboard'),
    path('ui/students/', TemplateView.as_view(template_name='ui/students.html'), name='ui_students'),
    path('ui/attendance/', TemplateView.as_view(template_name='ui/attendance.html'), name='ui_attendance'),
    path('ui/reports/', TemplateView.as_view(template_name='ui/reports.html'), name='ui_reports'),
    path('admin/',          admin.site.urls),
    path('api/auth/',       include('accounts.urls')),
    path('api/students/',   include('students.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/reports/',    include('reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)