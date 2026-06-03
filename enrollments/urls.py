from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('video/<int:video_id>/complete/', views.mark_video_complete_view, name='mark_video_complete'),
]

