from django.urls import path
from . import views

urlpatterns = [
    # Class endpoints
    path('classes/',              views.ClassListCreateView.as_view(),  name='class_list'),
    path('classes/<int:pk>/',     views.ClassDetailView.as_view(),      name='class_detail'),

    # Student endpoints
    path('',                      views.StudentListCreateView.as_view(), name='student_list'),
    path('<int:pk>/',             views.StudentDetailView.as_view(),     name='student_detail'),
    path('class/<int:class_id>/', views.StudentsByClassView.as_view(),   name='students_by_class'),
]