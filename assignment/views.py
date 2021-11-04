import os
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import fields, query
from django.forms.forms import Form
from django.http.response import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls.base import reverse, reverse_lazy
from django.views.generic import base
from django.views.generic.edit import DeleteView, FormMixin, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from assignment.form import AssignmentForm
from assignment.models import Assignment, StudentAssignment
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

base_dir = getattr(settings, 'BASE_DIR', 'None')

class AssignmentListView(LoginRequiredMixin, ListView):
    login_url = '/login'
    redirect_field_name = 'assignment'
    template_name = 'assignment/assignment_list.html'
    model = Assignment
    context_object_name = 'assignment'


class AssignmentDetailView(LoginRequiredMixin, DetailView, FormMixin):
    login_url = '/login'
    redirect_field_name = 'assignment'
    template_name = 'assignment/assignment_detail.html'
    model = Assignment
    form_class = AssignmentForm
    context_object_name = 'assignment'


    def get_context_data(self, **kwargs):
        stdId = str(self.request.user).split("@")[0]
        current_assignment = Assignment.objects.filter(id=self.assignment_id)[0]
        kwargs["is_deadline"] = current_assignment.is_deadline
        try:
            obj = StudentAssignment.objects.filter(stdId=stdId, assignment=current_assignment)
            if obj:
                kwargs["is_uploaded"] = True
                kwargs["data"] = obj[0]
            else:
                kwargs["is_uploaded"] = False
        except ObjectDoesNotExist:
            kwargs["is_uploaded"] = False
        return super().get_context_data(**kwargs)
    
    def get(self, request, *args, **kwargs):
        self.assignment_id = kwargs["pk"]
        return super().get(request, *args, **kwargs)
    

    def post(self, request, *args, **kwargs):
        stdId = str(self.request.user).split("@")[0]
        if not request.user.is_authenticated:
            return HttpResponseForbidden

        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.stdId = stdId
            instance.assignment = Assignment.objects.filter(id=kwargs['pk'])[0]
            instance.file.name = f"{instance.assignment.name}/{instance.file.name}"
            instance.save()
            return redirect("/assignment")


class AssignmentUpload(LoginRequiredMixin, base.TemplateView, FormMixin):
    login_url = '/login'
    redirect_field_name = 'assignment'
    template_name = 'assignment/assignment_upload.html'
    model = Assignment
    form_class = AssignmentForm
    def get_context_data(self, **kwargs):
        stdId = str(self.request.user).split("@")[0]
        current_assignment = Assignment.objects.filter(id=self.assignment_id)[0]
        kwargs['assignment_id'] = self.assignment_id
        try:
            obj = StudentAssignment.objects.filter(stdId=stdId, assignment=current_assignment)
            if obj:
                kwargs["is_uploaded"] = True
                kwargs["data"] = obj[0]
            else:
                kwargs["is_uploaded"] = False
        except ObjectDoesNotExist:
            kwargs["is_uploaded"] = False
        return super().get_context_data(**kwargs)
    
    def get(self, request, *args, **kwargs):
        self.assignment_id = kwargs["pk"]
        return super().get(request, *args, **kwargs)
    

    def post(self, request, *args, **kwargs):
        stdId = str(self.request.user).split("@")[0]
        if not request.user.is_authenticated:
            return HttpResponseForbidden

        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.stdId = stdId
            instance.assignment = Assignment.objects.filter(id=kwargs['pk'])[0]
            instance.file.name = f"{instance.assignment.name}/{instance.file.name}"
            instance.save()
            return redirect("/assignment")


class AssignmentUpdate(UpdateView):
    template_name = 'assignment/assignment_update.html'
    model = StudentAssignment
    form_class = AssignmentForm
    success_url= '/assignment'
    
    def get_object(self, queryset=None):
        stdId = str(self.request.user).split("@")[0]
        current_assignment = Assignment.objects.get(id=self.kwargs['pk'])
        return self.model.objects.get(stdId=stdId, assignment=current_assignment)
        
class AssignmentDelete(DeleteView):
    model = StudentAssignment
    template_name = 'assignment/assignment_delete.html'
    success_url = reverse_lazy('assignment:assignment-list')

    def get_object(self, queryset=None):
        stdId = str(self.request.user).split("@")[0]
        current_assignment = Assignment.objects.get(id=self.kwargs['pk'])
        return self.model.objects.get(stdId=stdId, assignment=current_assignment)