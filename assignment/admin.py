from django.contrib import admin
from django.urls.base import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.urls import reverse

class AssignmentAdmin(admin.ModelAdmin):
    list_display= ('name', 'view_student_links', )
    exclude = ('file', )
    def view_student_links(self, object):
        count = object.assignment.count()
        url = (
            reverse('admin:assignment_studentassignment_changelist')
            + "?"
            + urlencode({'assignment__id__exact': f"{object.id}"})
        )
        return format_html('<a href="{}">{} 份</a>', url, count)
    
    view_student_links.short_description = "已繳交數量"
    
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

class StudentAdmin(admin.ModelAdmin):
    exclude = ('assignment', )
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}
        