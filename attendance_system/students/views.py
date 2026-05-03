from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Student, Class
from .serializers import StudentSerializer, StudentListSerializer, ClassSerializer
from accounts.permissions import IsAdmin, IsAdminOrTeacher


# ─── Class Views ────────────────────────────────────────────────

class ClassListCreateView(generics.ListCreateAPIView):
    queryset = Class.objects.select_related('teacher').all()
    serializer_class = ClassSerializer
    permission_classes = [IsAdminOrTeacher]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'section']
    ordering_fields = ['name', 'section']


class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAdminOrTeacher]


# ─── Student Views ───────────────────────────────────────────────

class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.select_related('assigned_class').all()
    permission_classes = [IsAdminOrTeacher]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assigned_class', 'gender', 'is_active']
    search_fields = ['first_name', 'last_name', 'student_id', 'email']
    ordering_fields = ['first_name', 'last_name', 'created_at']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StudentListSerializer
        return StudentSerializer


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related('assigned_class').all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrTeacher]

    def destroy(self, request, *args, **kwargs):
        student = self.get_object()
        student.is_active = False   # Soft delete
        student.save()
        return Response(
            {"message": f"Student {student.full_name} deactivated."},
            status=status.HTTP_200_OK
        )


class StudentsByClassView(generics.ListAPIView):
    """Get all active students in a specific class."""
    serializer_class = StudentListSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        class_id = self.kwargs['class_id']
        return Student.objects.filter(
            assigned_class_id=class_id, is_active=True
        ).select_related('assigned_class')