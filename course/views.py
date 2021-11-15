from typing import List
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from assignment.models import Assignment
from course.models import Course

class CourseListView(ListView):
    template_name = 'course/course_list.html'
    model = Course
    context_object_name = 'course'


class CourseDetailView(DetailView):
    template_name = 'course/course_detail.html'
    model = Course
    context_object_name = 'course'

    def get(self, request, *args, **kwargs):
        self.pk = kwargs["pk"]
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs["assignment"] = Assignment.objects.filter(course__id=self.pk)
        return super().get_context_data(**kwargs)

