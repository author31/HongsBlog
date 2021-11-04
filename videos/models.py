import os
from django.db import models
from datetime import datetime
from functools import partial
from django.urls import reverse
# Create your models here.

def _update_filename(instance, filename, path):
    path = path
    return os.path.join(path, filename)

def get_full_path(path):
    return partial(_update_filename, path=path)

class VideoMaterial(models.Model):
    title= models.CharField('標題', max_length=30, null=False, blank=False)
    description = models.TextField('描述', null=True, blank=True)
    deadline = models.DateTimeField('播放期限', null=False, blank=False)
    video_file = models.FileField('影片', null=False, blank=False, upload_to=get_full_path('videos-material/'))
    
    def is_deadline(self):
        return datetime.now() > self.deadline

    def get_absolute_url(self):
        return reverse('videos:video-detail', args=[self.id])

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = '影片教材'
        verbose_name_plural = '影片教材'