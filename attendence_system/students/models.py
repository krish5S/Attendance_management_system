from django.db import models
from accounts.models import User


class Class(models.Model):
    name = models.CharField(max_length=100)          # e.g. "10th Grade"
    section = models.CharField(max_length=10)        # e.g. "A"
    teacher = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='classes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('name', 'section')
        ordering = ['name', 'section']

    def __str__(self):
        return f"{self.name} - {self.section}"


class Student(models.Model):
    GENDER_CHOICES = (('M', 'Male'), ('F', 'Female'), ('O', 'Other'))

    student_id = models.CharField(max_length=20, unique=True)  # e.g. STU001
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='students/', blank=True, null=True)
    assigned_class = models.ForeignKey(
        Class, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='students'
    )
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"