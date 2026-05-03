from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


admin.site.site_header = "Attendance Management System"
admin.site.site_title  = "AMS Admin Portal"
admin.site.index_title = "Welcome to AMS Admin"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',    include('accounts.urls')),
    path('api/students/', include('students.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/reports/',  include('reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
