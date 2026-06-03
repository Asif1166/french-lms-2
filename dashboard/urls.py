from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('my-courses/', views.my_courses_view, name='my_courses'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('faqs/', views.faq_list_view, name='faq_list'),
    path('faqs/<slug:category_slug>/', views.faq_list_view, name='faq_category'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('contact/', views.contact_view, name='contact'),
    path('instructors/', views.instructor_list_view, name='instructors'),
    path('instructors/<int:pk>/', views.instructor_detail_view, name='instructor_detail'),
    path('community-stories/<int:pk>/', views.community_story_detail_view, name='community_story_detail'),
    path('success-stories/', views.success_story_list_view, name='success_stories'),
]

