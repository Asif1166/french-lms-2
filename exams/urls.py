from django.urls import path
from . import views

app_name = 'exams'

urlpatterns = [
    path('submit/<int:video_id>/', views.submit_answers_view, name='submit_answers'),
    path('submissions/review/', views.submission_review_view, name='submission_review'),
    path('submissions/<int:submission_id>/review/', views.review_submission_view, name='review_submission'),
    path('mock-exams/', views.mock_exam_list_view, name='mock_exam_list'),
    path('mock-exams/<int:exam_id>/', views.mock_exam_detail_view, name='mock_exam_detail'),
    path('mock-exams/<int:exam_id>/start/', views.start_mock_exam_view, name='start_mock_exam'),
    path('mock-exams/<int:exam_id>/take/<int:attempt_id>/', views.take_mock_exam_view, name='take_mock_exam'),
    path('mock-exams/<int:exam_id>/submit/<int:attempt_id>/', views.submit_mock_exam_view, name='submit_mock_exam'),
    path('mock-exams/<int:exam_id>/result/<int:attempt_id>/', views.mock_exam_result_view, name='mock_exam_result'),
    # Pricing URLs
    path('pricing/', views.pricing_view, name='pricing'),
    path('purchase/<int:package_id>/', views.purchase_package_view, name='purchase_package'),
    path('my-purchases/', views.my_purchases_view, name='my_purchases'),
    # Payment URLs
    path('payment/success/', views.payment_success_view, name='payment_success'),
    path('webhook/stripe/', views.stripe_webhook_view, name='stripe_webhook'),
]

