from django.contrib import admin
from django.urls.base import reverse
from django.utils.html import format_html
from assignment.models import Assignment
from course.models import Course
from videos.models import VideoMaterial

class AssignmentStack(admin.StackedInline):
    model = Assignment
    extra = 0

class VideoStack(admin.StackedInline):
    model = VideoMaterial
    extra = 0
    
class CourseAdmin(admin.ModelAdmin):
    inlines = [AssignmentStack, VideoStack]
    model = Course
    list_display = ('name', 'view_assignment', )

    def view_assignment(self, object):
        url = reverse('admin:assignment_assignment_changelist')
        return format_html('<a href="{}">{}</a>', url, '檢視作業')
    
    view_assignment.short_description = '作業'