from django.db.models import Count, Q, F
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from attendance.models import Attendance, AttendanceSession
from students.models import Student, Class
from accounts.permissions import IsAdminOrTeacher


# ── Helper ────────────────────────────────────────────────────────

def attendance_summary(qs):
    total   = qs.count()
    present = qs.filter(status='P').count()
    absent  = qs.filter(status='A').count()
    late    = qs.filter(status='L').count()
    excused = qs.filter(status='E').count()
    percentage = round((present / total) * 100, 2) if total else 0
    return {
        "total":      total,
        "present":    present,
        "absent":     absent,
        "late":       late,
        "excused":    excused,
        "percentage": percentage,
    }


# ── 1. Student Attendance Report ─────────────────────────────────

class StudentAttendanceReportView(APIView):
    """
    GET /api/reports/student/<student_id>/
    Query params: start_date, end_date, class_ref
    """
    permission_classes = [IsAdminOrTeacher]

    def get(self, request, student_id):
        try:
            student = Student.objects.get(pk=student_id, is_active=True)
        except Student.DoesNotExist:
            return Response({"error": "Student not found."}, status=404)

        qs = Attendance.objects.filter(student=student)

        start_date = request.query_params.get('start_date')
        end_date   = request.query_params.get('end_date')
        class_ref  = request.query_params.get('class_ref')

        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        if class_ref:
            qs = qs.filter(class_ref_id=class_ref)

        # Per-day breakdown
        records = qs.order_by('date').values(
            'date', 'status', 'class_ref__name',
            'class_ref__section', 'remarks'
        )

        return Response({
            "student": {
                "id":         student.id,
                "student_id": student.student_id,
                "name":       student.full_name,
                "class":      str(student.assigned_class),
            },
            "summary":  attendance_summary(qs),
            "records":  list(records),
        })


# ── 2. Class Attendance Report ────────────────────────────────────

class ClassAttendanceReportView(APIView):
    """
    GET /api/reports/class/<class_id>/
    Query params: start_date, end_date
    """
    permission_classes = [IsAdminOrTeacher]

    def get(self, request, class_id):
        try:
            cls = Class.objects.get(pk=class_id)
        except Class.DoesNotExist:
            return Response({"error": "Class not found."}, status=404)

        qs = Attendance.objects.filter(class_ref=cls)

        start_date = request.query_params.get('start_date')
        end_date   = request.query_params.get('end_date')
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)

        # Per-student summary
        students = Student.objects.filter(
            assigned_class=cls, is_active=True
        )
        student_summaries = []
        for s in students:
            s_qs = qs.filter(student=s)
            summary = attendance_summary(s_qs)
            summary.update({
                "student_id": s.student_id,
                "name":       s.full_name,
            })
            student_summaries.append(summary)

        # Sort by attendance % descending
        student_summaries.sort(key=lambda x: x['percentage'], reverse=True)

        return Response({
            "class":    {"id": cls.id, "name": str(cls)},
            "summary":  attendance_summary(qs),
            "students": student_summaries,
        })


# ── 3. Daily Attendance Report ────────────────────────────────────

class DailyAttendanceReportView(APIView):
    """
    GET /api/reports/daily/
    Query params: date (required), class_ref (optional)
    """
    permission_classes = [IsAdminOrTeacher]

    def get(self, request):
        date      = request.query_params.get('date')
        class_ref = request.query_params.get('class_ref')

        if not date:
            return Response({"error": "date query param is required."}, status=400)

        qs = Attendance.objects.filter(date=date).select_related(
            'student', 'class_ref'
        )
        if class_ref:
            qs = qs.filter(class_ref_id=class_ref)

        records = qs.values(
            'student__student_id',
            'student__first_name',
            'student__last_name',
            'class_ref__name',
            'class_ref__section',
            'status',
            'remarks',
        )

        return Response({
            "date":    date,
            "summary": attendance_summary(qs),
            "records": list(records),
        })


# ── 4. Monthly Attendance Report ──────────────────────────────────

class MonthlyAttendanceReportView(APIView):
    """
    GET /api/reports/monthly/
    Query params: year, month, class_ref (optional)
    """
    permission_classes = [IsAdminOrTeacher]

    def get(self, request):
        year      = request.query_params.get('year')
        month     = request.query_params.get('month')
        class_ref = request.query_params.get('class_ref')

        if not year or not month:
            return Response({"error": "year and month are required."}, status=400)

        qs = Attendance.objects.filter(
            date__year=year, date__month=month
        )
        if class_ref:
            qs = qs.filter(class_ref_id=class_ref)

        # Group by date
        by_date = (
            qs.values('date')
            .annotate(
                present=Count('id', filter=Q(status='P')),
                absent=Count('id',  filter=Q(status='A')),
                late=Count('id',    filter=Q(status='L')),
                total=Count('id'),
            )
            .order_by('date')
        )

        return Response({
            "year":     year,
            "month":    month,
            "summary":  attendance_summary(qs),
            "by_date":  list(by_date),
        })


# ── 5. Low Attendance Alert ───────────────────────────────────────

class LowAttendanceAlertView(APIView):
    """
    GET /api/reports/low-attendance/
    Query params: threshold (default 75), class_ref, start_date, end_date
    """
    permission_classes = [IsAdminOrTeacher]

    def get(self, request):
        threshold  = float(request.query_params.get('threshold', 75))
        class_ref  = request.query_params.get('class_ref')
        start_date = request.query_params.get('start_date')
        end_date   = request.query_params.get('end_date')

        students = Student.objects.filter(is_active=True)
        if class_ref:
            students = students.filter(assigned_class_id=class_ref)

        alerts = []
        for student in students:
            qs = Attendance.objects.filter(student=student)
            if start_date:
                qs = qs.filter(date__gte=start_date)
            if end_date:
                qs = qs.filter(date__lte=end_date)

            total   = qs.count()
            present = qs.filter(status='P').count()
            if total == 0:
                continue

            pct = round((present / total) * 100, 2)
            if pct < threshold:
                alerts.append({
                    "student_id":  student.student_id,
                    "name":        student.full_name,
                    "class":       str(student.assigned_class),
                    "total":       total,
                    "present":     present,
                    "percentage":  pct,
                    "shortage":    round(threshold - pct, 2),
                })

        alerts.sort(key=lambda x: x['percentage'])

        return Response({
            "threshold": threshold,
            "total_alerts": len(alerts),
            "alerts": alerts,
        })


# ── 6. Dashboard Summary ──────────────────────────────────────────

class DashboardSummaryView(APIView):
    """
    GET /api/reports/dashboard/
    Returns high-level system stats.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.utils import timezone
        today = timezone.localdate()

        total_students  = Student.objects.filter(is_active=True).count()
        total_classes   = Class.objects.count()
        today_qs        = Attendance.objects.filter(date=today)
        today_present   = today_qs.filter(status='P').count()
        today_absent    = today_qs.filter(status='A').count()
        today_sessions  = AttendanceSession.objects.filter(date=today).count()

        return Response({
            "today":           str(today),
            "total_students":  total_students,
            "total_classes":   total_classes,
            "today_present":   today_present,
            "today_absent":    today_absent,
            "today_sessions":  today_sessions,
            "today_summary":   attendance_summary(today_qs),
        })