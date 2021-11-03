from django.urls.conf import path


from django.urls import path
from .views import *

app_name = 'videos'

urlpatterns = [
    path(r"", VideoListView.as_view(), name='video-list'),
    path(r"<int:pk>", VideoDetailView.as_view(), name='video-detail')
]