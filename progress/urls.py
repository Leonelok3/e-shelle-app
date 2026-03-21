from django.urls import path
from . import views

app_name = "progress"

urlpatterns = [
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("parent/", views.parent_dashboard, name="parent_dashboard"),
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
]
