from django.db import models
from django.db.models.fields import related
from django.utils.timezone import now
from django.urls import reverse

# Create your models here.
from pathlib import Path
from django.conf import settings
import os
from functools import partial 
from datetime import datetime


def _update_filename(instance, filename, path):
    path = path
    return os.path.join(path, filename)

def get_full_path(path):
    return partial(_update_filename, path=path)

class Assignment(models.Model):
    name = models.CharField("作業名稱", max_length=100, null=False, blank=False)
    description = models.TextField("描述",null=True)
    deadline = models.DateTimeField('期限', blank=False, null=False, default=now)
    course = models.ForeignKey('course.Course', on_delete=models.CASCADE, related_name='course', null=True)
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '作業'
        verbose_name_plural = '作業'

    def get_absolute_url(self):
        return reverse('assignment:assignment-detail', args=[self.id])

    def is_deadline(self):
        return datetime.now() > self.deadline

class StudentAssignment(models.Model):
    stdId = models.CharField("學號", null=False, blank=False, max_length=10)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='assignment', verbose_name="作業")
    file = models.FileField("附件", blank=True, upload_to=get_full_path(f'assignment/'),)
    content = models.TextField('內容', blank=False, null= True)

    class Meta:
        verbose_name = '已繳學生'
        verbose_name_plural = '已繳學生'
    
    def __str__(self) -> str:
        return self.stdId
    
