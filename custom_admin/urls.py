from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # Auth
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Level Codes
    path('level-codes/', views.level_code_list, name='level_code_list'),
    path('level-codes/create/', views.level_code_create, name='level_code_create'),
    path('level-codes/<int:pk>/edit/', views.level_code_edit, name='level_code_edit'),
    path('level-codes/<int:pk>/delete/', views.level_code_delete, name='level_code_delete'),

    # Levels
    path('levels/', views.level_list, name='level_list'),
    path('levels/create/', views.level_create, name='level_create'),
    path('levels/<int:pk>/edit/', views.level_edit, name='level_edit'),
    path('levels/<int:pk>/delete/', views.level_delete, name='level_delete'),

    # Chapters
    path('chapters/', views.chapter_list, name='chapter_list'),
    path('chapters/create/', views.chapter_create, name='chapter_create'),
    path('chapters/<int:pk>/edit/', views.chapter_edit, name='chapter_edit'),
    path('chapters/<int:pk>/delete/', views.chapter_delete, name='chapter_delete'),

    # Video Lessons
    path('video-lessons/', views.video_lesson_list, name='video_lesson_list'),
    path('video-lessons/create/', views.video_lesson_create, name='video_lesson_create'),
    path('video-lessons/<int:pk>/edit/', views.video_lesson_edit, name='video_lesson_edit'),
    path('video-lessons/<int:pk>/delete/', views.video_lesson_delete, name='video_lesson_delete'),

    # Lesson Resources
    path('lesson-resources/', views.lesson_resource_list, name='lesson_resource_list'),
    path('lesson-resources/create/', views.lesson_resource_create, name='lesson_resource_create'),
    path('lesson-resources/<int:pk>/edit/', views.lesson_resource_edit, name='lesson_resource_edit'),
    path('lesson-resources/<int:pk>/delete/', views.lesson_resource_delete, name='lesson_resource_delete'),

    # Word Meanings
    path('word-meanings/', views.word_meaning_list, name='word_meaning_list'),
    path('word-meanings/create/', views.word_meaning_create, name='word_meaning_create'),
    path('word-meanings/<int:pk>/edit/', views.word_meaning_edit, name='word_meaning_edit'),
    path('word-meanings/<int:pk>/delete/', views.word_meaning_delete, name='word_meaning_delete'),

    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
]
