from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('create/<int:course_id>/', views.create_payment_view, name='create_payment'),
    path('create-level/<int:level_id>/', views.create_level_payment_view, name='create_level_payment'),
    path('success/', views.payment_success_view, name='payment_success'),
    path('cancel/', views.payment_cancel_view, name='payment_cancel'),
    path('webhook/stripe/', views.stripe_webhook_view, name='stripe_webhook'),
]

