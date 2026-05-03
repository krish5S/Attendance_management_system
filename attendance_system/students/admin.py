from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Class


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display  = ('name', 'section', 'teacher', 'student_count', 'created_at')
    list_filter   = ('name',)
    search_fields = ('name', 'section', 'teacher__username')
    ordering      = ('name', 'section')

    def student_count(self, obj):
        count = obj.students.filter(is_active=True).count()
        return format_html('<b>{}</b>', count)
    student_count.short_description = 'Active Students'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display   = (
        'student_id', 'full_name', 'gender',
        'assigned_class', 'guardian_phone', 'status_badge'
    )
    list_filter    = ('gender', 'assigned_class', 'is_active')
    search_fields  = ('student_id', 'first_name', 'last_name', 'email')
    ordering       = ('first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Info', {
            'fields': (
                'student_id', 'first_name', 'last_name',
                'gender', 'date_of_birth', 'profile_picture'
            )
        }),
        ('Contact', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Class & Guardian', {
            'fields': (
                'assigned_class', 'guardian_name', 'guardian_phone'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

    def status_badge(self, obj):
        color = 'green' if obj.is_active else 'red'
        label = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="color:{}; font-weight:bold;">{}</span>', color, label
        )
    status_badge.short_description = 'Status'