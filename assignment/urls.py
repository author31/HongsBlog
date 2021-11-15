from django.urls.conf import path


from django.urls import path
from .views import *

app_name = 'assignment'

urlpatterns = [
    # path(r"", 
    #     AssignmentListView.as_view(),
    #     name='assignment-list'),
    path(r"<int:pk>",
        AssignmentDetailView.as_view(),
        name='assignment-detail'
    ),
    path(r"upload/<int:pk>",
        AssignmentUpload.as_view(),
        name='assignment-upload'
    ),
    path(r"update/<int:pk>",
        AssignmentUpdate.as_view(),
        name='assignment-update'
    ),
    path(r"delete/<int:pk>",
        AssignmentDelete.as_view(),
        name='assignment-delete'
    ),

]