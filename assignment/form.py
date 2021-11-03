from django import forms
from assignment.models import StudentAssignment
from django.utils.translation import ugettext_lazy as _

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = StudentAssignment
        fields = ['content', 'file', ]
        labels = {
            'file_upload': _('附件'),
        }
