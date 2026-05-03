from django.contrib import admin
from .models import Student, Class


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'teacher', 'created_at')
    list_filter = ('name',)
    search_fields = ('name', 'section')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'gender', 'assigned_class', 'is_active')
    list_filter = ('gender', 'assigned_class', 'is_active')
    search_fields = ('student_id', 'first_name', 'last_name', 'email')