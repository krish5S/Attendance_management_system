from django.contrib import admin
from .models import Attendance, AttendanceSession


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_ref', 'date', 'status', 'marked_by')
    list_filter  = ('status', 'date', 'class_ref')
    search_fields = ('student__first_name', 'student__last_name', 'student__student_id')
    date_hierarchy = 'date'


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('class_ref', 'date', 'marked_by', 'is_finalized', 'created_at')
    list_filter  = ('is_finalized', 'class_ref')