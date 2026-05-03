from django.db import models
from students.models import Student, Class
from accounts.models import User


class Attendance(models.Model):
    STATUS_CHOICES = (
        ('P', 'Present'),
        ('A', 'Absent'),
        ('L', 'Late'),
        ('E', 'Excused'),
    )

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        related_name='attendances'
    )
    class_ref = models.ForeignKey(
        Class, on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='A')
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='marked_attendances'
    )
    remarks = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'date', 'class_ref')
        ordering = ['-date', 'student']

    def __str__(self):
        return f"{self.student} | {self.date} | {self.get_status_display()}"


class AttendanceSession(models.Model):
    """Tracks a bulk attendance session for a class on a given date."""
    class_ref = models.ForeignKey(
        Class, on_delete=models.CASCADE,
        related_name='sessions'
    )
    date = models.DateField()
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sessions'
    )
    is_finalized = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('class_ref', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.class_ref} | {self.date}"