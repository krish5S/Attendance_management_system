from django.db import transaction
from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Attendance, AttendanceSession
from .serializers import (
    AttendanceSerializer,
    BulkAttendanceSerializer,
    AttendanceSessionSerializer,
)
from accounts.permissions import IsAdminOrTeacher


# ── Single record CRUD ────────────────────────────────────────────

class AttendanceListCreateView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['student', 'class_ref', 'date', 'status']
    ordering_fields = ['date', 'created_at']

    def get_queryset(self):
        return Attendance.objects.select_related(
            'student', 'class_ref', 'marked_by'
        ).all()

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)


class AttendanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.select_related(
        'student', 'class_ref', 'marked_by'
    ).all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrTeacher]

    def perform_update(self, serializer):
        serializer.save(marked_by=self.request.user)


# ── Bulk mark attendance ──────────────────────────────────────────

class BulkMarkAttendanceView(APIView):
    permission_classes = [IsAdminOrTeacher]

    @transaction.atomic
    def post(self, request):
        serializer = BulkAttendanceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data      = serializer.validated_data
        class_id  = data['class_ref']
        date      = data['date']
        records   = data['attendance']

        # Create or update session
        session, _ = AttendanceSession.objects.get_or_create(
            class_ref_id=class_id,
            date=date,
            defaults={'marked_by': request.user}
        )

        if session.is_finalized:
            return Response(
                {"error": "Attendance for this class and date is already finalized."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created, updated = 0, 0
        for record in records:
            obj, is_new = Attendance.objects.update_or_create(
                student_id=record['student'],
                class_ref_id=class_id,
                date=date,
                defaults={
                    'status': record['status'],
                    'remarks': record.get('remarks', ''),
                    'marked_by': request.user,
                }
            )
            if is_new:
                created += 1
            else:
                updated += 1

        return Response({
            "message": "Attendance marked successfully.",
            "session_id": session.id,
            "date": str(date),
            "created": created,
            "updated": updated,
        }, status=status.HTTP_200_OK)


# ── Finalize session ──────────────────────────────────────────────

class FinalizeSessionView(APIView):
    permission_classes = [IsAdminOrTeacher]

    def post(self, request, session_id):
        try:
            session = AttendanceSession.objects.get(pk=session_id)
        except AttendanceSession.DoesNotExist:
            return Response({"error": "Session not found."}, status=status.HTTP_404_NOT_FOUND)

        if session.is_finalized:
            return Response({"error": "Already finalized."}, status=status.HTTP_400_BAD_REQUEST)

        session.is_finalized = True
        session.save()
        return Response({"message": "Session finalized."}, status=status.HTTP_200_OK)


# ── Session list ──────────────────────────────────────────────────

class AttendanceSessionListView(generics.ListAPIView):
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['class_ref', 'date', 'is_finalized']
    ordering_fields = ['date', 'created_at']

    def get_queryset(self):
        return AttendanceSession.objects.select_related(
            'class_ref', 'marked_by'
        ).all()