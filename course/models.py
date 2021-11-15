from django.db import models
from assignment.models import Assignment
from videos.models import VideoMaterial
from django.urls import reverse
from django.utils.timezone import now

class Course(models.Model):
    name = models.CharField('課程名稱', max_length=30, null=False, blank=False)
    deadline = models.DateTimeField('期限', blank=False, null=False, default=now)
    def __str__(self) -> str:
        return self.name
    
    def get_absolute_url(self):
        return reverse('course:course-detail', args= [self.id])
    
    class Meta:
        verbose_name= '課程'
        verbose_name_plural= '課程'
