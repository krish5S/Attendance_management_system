from django.contrib import admin
from django.utils.html import format_html
from .models import Attendance, AttendanceSession


STATUS_COLORS = {
    'P': 'green',
    'A': 'red',
    'L': 'orange',
    'E': 'blue',
}


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display   = (
        'student', 'class_ref', 'date',
        'colored_status', 'marked_by', 'remarks'
    )
    list_filter    = ('status', 'date', 'class_ref')
    search_fields  = (
        'student__first_name', 'student__last_name',
        'student__student_id'
    )
    date_hierarchy = 'date'
    ordering       = ('-date',)
    readonly_fields = ('created_at', 'updated_at')

    def colored_status(self, obj):
        color = STATUS_COLORS.get(obj.status, 'black')
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>',
            color, obj.get_status_display()
        )
    colored_status.short_description = 'Status'


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display  = (
        'class_ref', 'date', 'marked_by',
        'finalized_badge', 'created_at'
    )
    list_filter   = ('is_finalized', 'class_ref')
    search_fields = ('class_ref__name',)
    ordering      = ('-date',)

    def finalized_badge(self, obj):
        color = 'green' if obj.is_finalized else 'orange'
        label = 'Finalized' if obj.is_finalized else 'Pending'
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>', color, label
        )
    finalized_badge.short_description = 'Session Status'