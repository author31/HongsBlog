from django.urls import path
from course.views import *

app_name = 'course'

urlpatterns = [
    path(r"", CourseListView.as_view(), name='course-list'),
    path(r"<int:pk>", CourseDetailView.as_view(), name='course-detail'),
]