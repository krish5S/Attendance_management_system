from rest_framework import serializers
from .models import Attendance, AttendanceSession
from students.serializers import StudentListSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source='student.full_name', read_only=True
    )
    student_id = serializers.CharField(
        source='student.student_id', read_only=True
    )
    marked_by_name = serializers.CharField(
        source='marked_by.get_full_name', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )

    class Meta:
        model = Attendance
        fields = (
            'id', 'student', 'student_name', 'student_id',
            'class_ref', 'date', 'status', 'status_display',
            'marked_by', 'marked_by_name', 'remarks',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'marked_by', 'created_at', 'updated_at')


# ── Single record inside a bulk payload ──────────────────────────
class BulkAttendanceRecordSerializer(serializers.Serializer):
    student = serializers.IntegerField()
    status  = serializers.ChoiceField(choices=['P', 'A', 'L', 'E'])
    remarks = serializers.CharField(required=False, allow_blank=True)


# ── Full bulk-mark payload ────────────────────────────────────────
class BulkAttendanceSerializer(serializers.Serializer):
    class_ref   = serializers.IntegerField()
    date        = serializers.DateField()
    attendance  = BulkAttendanceRecordSerializer(many=True)

    def validate(self, attrs):
        from students.models import Student, Class
        try:
            Class.objects.get(pk=attrs['class_ref'])
        except Class.DoesNotExist:
            raise serializers.ValidationError({"class_ref": "Class not found."})

        student_ids = [r['student'] for r in attrs['attendance']]
        found = Student.objects.filter(
            pk__in=student_ids, is_active=True
        ).count()
        if found != len(student_ids):
            raise serializers.ValidationError(
                {"attendance": "One or more student IDs are invalid or inactive."}
            )
        return attrs


class AttendanceSessionSerializer(serializers.ModelSerializer):
    class_name   = serializers.CharField(source='class_ref.__str__', read_only=True)
    marked_by_name = serializers.CharField(
        source='marked_by.get_full_name', read_only=True
    )
    total_present = serializers.SerializerMethodField()
    total_absent  = serializers.SerializerMethodField()
    total_late    = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSession
        fields = (
            'id', 'class_ref', 'class_name', 'date',
            'marked_by', 'marked_by_name', 'is_finalized',
            'total_present', 'total_absent', 'total_late', 'created_at'
        )
        read_only_fields = ('id', 'marked_by', 'created_at')

    def _qs(self, obj, status):
        return Attendance.objects.filter(
            class_ref=obj.class_ref, date=obj.date, status=status
        ).count()

    def get_total_present(self, obj): return self._qs(obj, 'P')
    def get_total_absent(self, obj):  return self._qs(obj, 'A')
    def get_total_late(self, obj):    return self._qs(obj, 'L')