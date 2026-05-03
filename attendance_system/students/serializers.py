from rest_framework import serializers
from .models import Student, Class


class ClassSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(
        source='teacher.get_full_name', read_only=True
    )
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = ('id', 'name', 'section', 'teacher',
                  'teacher_name', 'student_count', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_student_count(self, obj):
        return obj.students.filter(is_active=True).count()


class StudentSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    class_name = serializers.CharField(
        source='assigned_class.__str__', read_only=True
    )

    class Meta:
        model = Student
        fields = (
            'id', 'student_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'gender', 'date_of_birth', 'address',
            'profile_picture', 'assigned_class', 'class_name',
            'guardian_name', 'guardian_phone', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'full_name', 'class_name', 'created_at', 'updated_at')


class StudentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    full_name = serializers.ReadOnlyField()
    class_name = serializers.CharField(
        source='assigned_class.__str__', read_only=True
    )

    class Meta:
        model = Student
        fields = ('id', 'student_id', 'full_name', 'gender',
                  'assigned_class', 'class_name', 'is_active')