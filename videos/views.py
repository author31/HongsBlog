from django.db.models import base
from django.shortcuts import redirect, render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from videos.models import VideoMaterial

class VideoListView(ListView):
    template_name = 'videos/video-list.html'
    context_object_name = 'videos'
    model = VideoMaterial


class VideoDetailView(DetailView):
    template_name = 'videos/video-detail.html'
    context_object_name = 'videos'
    model = VideoMaterial

    def get(self, request, *args, **kwarg):
        vid = self.model.objects.get(id=kwarg['pk'])
        if vid.is_deadline():
            return redirect("/")
        return super().get(request, *args, **kwarg)