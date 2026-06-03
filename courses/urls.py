from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.level_list_view, name='level_list'),
    path('level/<int:level_id>/', views.level_detail_view, name='level_detail'),
    path('chapter/<int:chapter_id>/', views.chapter_detail_view, name='chapter_detail'),
    path('video/<int:video_id>/', views.video_detail_view, name='video_detail'),
    path('course/<int:course_id>/', views.course_detail_view, name='course_detail'),
    path('courses/', views.course_list_view, name='course_list'),
]

# URLs updated for course details

