from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import uuid

from .models import (
    Question, Option, Submission, MockExam, MockExamAttempt, 
    MockExamSection, MockExamQuestion, MockExamPackage, 
    MockExamPurchase, MockExamAccess
)
from courses.models import VideoLesson
from enrollments.models import Enrollment


@login_required
def submit_answers_view(request, video_id):
    """Handle question submissions"""
    video = get_object_or_404(VideoLesson, id=video_id)
    
    # Check enrollment
    has_access = False
    enrollments = Enrollment.objects.filter(user=request.user, status='ACTIVE')
    for enrollment in enrollments:
        if enrollment.has_access_to_level(video.chapter.level):
            has_access = True
            break
    
    if not has_access:
        messages.error(request, 'You need to enroll to submit answers')
        return redirect('courses:video_detail', video_id=video_id)
    
    if request.method == 'POST':
        questions = video.questions.filter(is_active=True)
        total_score = 0
        total_max_score = 0
        
        for question in questions:
            submission, created = Submission.objects.get_or_create(
                user=request.user,
                question=question,
                defaults={'max_score': question.marks}
            )
            
            total_max_score += float(question.marks)
            
            # Handle different question types
            if question.question_type in ['MCQ_SINGLE', 'MCQ_MULTIPLE', 'TRUE_FALSE', 'MATCHING']:
                # Auto-grading for MCQ and True/False
                selected_option_ids = request.POST.getlist(f'question_{question.id}') or [request.POST.get(f'question_{question.id}')]
                selected_option_ids = [id for id in selected_option_ids if id]
                
                if selected_option_ids:
                    selected_options = Option.objects.filter(id__in=selected_option_ids)
                    submission.selected_options.set(selected_options)
                    
                    # Check if all selected are correct and all correct are selected
                    correct_options = question.options.filter(is_correct=True)
                    if correct_options.count() == selected_options.count() and \
                       all(opt.is_correct for opt in selected_options):
                        submission.score = question.marks
                        submission.review_status = 'AUTO_GRADED'
                        total_score += float(question.marks)
                    else:
                        submission.score = 0
                        submission.review_status = 'AUTO_GRADED'
                else:
                    submission.score = 0
                    submission.review_status = 'AUTO_GRADED'
            
            elif question.question_type in ['YES_NO_NOT_MENTIONED']:
                answer = request.POST.get(f'question_{question.id}')
                # This would need correct answer stored in options
                submission.answer_text = answer
                submission.review_status = 'PENDING'
            
            elif question.question_type in ['FILL_BLANK', 'INFORMATION_EXTRACTION']:
                answer = request.POST.get(f'question_{question.id}')
                submission.answer_text = answer
                submission.review_status = 'PENDING'
            
            elif question.question_type in ['EMAIL_WRITING', 'SHORT_PARAGRAPH', 'OPINION_TEXT']:
                answer = request.POST.get(f'question_{question.id}')
                submission.answer_text = answer
                submission.review_status = 'PENDING'
            
            elif question.question_type in ['ROLE_PLAY', 'IMAGE_DESCRIPTION', 'TOPIC_MONOLOGUE']:
                if f'question_{question.id}_file' in request.FILES:
                    submission.file_upload = request.FILES[f'question_{question.id}_file']
                submission.review_status = 'PENDING'
            
            submission.save()
        
        messages.success(request, f'Answers submitted! Score: {total_score}/{total_max_score}')
        return redirect('courses:video_detail', video_id=video_id)
    
    return redirect('courses:video_detail', video_id=video_id)


@login_required
def submission_review_view(request):
    """Instructor view to review submissions"""
    if not (request.user.is_instructor() or request.user.is_admin()):
        messages.error(request, 'Access denied')
        return redirect('dashboard:home')
    
    submissions = Submission.objects.filter(
        review_status='PENDING'
    ).select_related('user', 'question').order_by('-submitted_at')
    
    context = {
        'submissions': submissions
    }
    return render(request, 'exams/submission_review.html', context)


@login_required
def review_submission_view(request, submission_id):
    """Review and grade a specific submission"""
    if not (request.user.is_instructor() or request.user.is_admin()):
        messages.error(request, 'Access denied')
        return redirect('dashboard:home')
    
    submission = get_object_or_404(Submission, id=submission_id)
    
    if request.method == 'POST':
        score = float(request.POST.get('score', 0))
        feedback = request.POST.get('feedback', '')
        
        submission.score = score
        submission.feedback = feedback
        submission.review_status = 'REVIEWED'
        submission.reviewed_by = request.user
        from django.utils import timezone
        submission.reviewed_at = timezone.now()
        submission.save()
        
        messages.success(request, 'Submission reviewed successfully')
        return redirect('exams:submission_review')
    
    context = {
        'submission': submission
    }
    return render(request, 'exams/review_submission.html', context)


@login_required
def mock_exam_list_view(request):
    """List all available mock exams with access check and sorting"""
    exams = list(MockExam.objects.filter(is_active=True).select_related('level'))
    
    # Get user access data
    enrolled_levels = []
    if request.user.is_authenticated:
        from enrollments.models import Enrollment
        from .models import MockExamAccess
        active_enrollments = Enrollment.objects.filter(user=request.user, status='ACTIVE')
        for enrollment in active_enrollments:
            if enrollment.level:
                enrolled_levels.append(enrollment.level.id)
            elif enrollment.course and enrollment.course.level:
                enrolled_levels.append(enrollment.course.level.id)

        
        # Direct access via purchase
        direct_access_ids = list(MockExamAccess.objects.filter(
            user=request.user, 
            is_active=True
        ).values_list('exam_id', flat=True))
    else:
        direct_access_ids = []

    # Attach access status and sort
    for exam in exams:
        exam.has_access = (exam.level_id in enrolled_levels) or (exam.id in direct_access_ids)
    
    # Sort: Accessible first, then by level, then by ID
    exams.sort(key=lambda x: (not x.has_access, x.level.code if x.level else '', x.id))

    context = {
        'exams': exams
    }
    return render(request, 'exams/mock_exam_list.html', context)


@login_required
def mock_exam_detail_view(request, exam_id):
    """Start or view mock exam"""
    exam = get_object_or_404(MockExam, id=exam_id, is_active=True)
    
    # Check enrollment
    has_access = False
    enrollments = Enrollment.objects.filter(user=request.user, status='ACTIVE')
    for enrollment in enrollments:
        if enrollment.has_access_to_level(exam.level):
            has_access = True
            break
    
    if not has_access:
        messages.warning(request, 'You need to enroll to take mock exams')
        return redirect('courses:course_list')
    
    # Get existing attempt or create new one
    attempt = MockExamAttempt.objects.filter(
        user=request.user,
        exam=exam
    ).order_by('-started_at').first()
    
    context = {
        'exam': exam,
        'attempt': attempt
    }
    return render(request, 'exams/mock_exam_detail.html', context)


@login_required
def start_mock_exam_view(request, exam_id):
    """Start a new mock exam attempt"""
    exam = get_object_or_404(MockExam, id=exam_id, is_active=True)
    
    # Check enrollment
    has_access = False
    enrollments = Enrollment.objects.filter(user=request.user, status='ACTIVE')
    for enrollment in enrollments:
        if enrollment.has_access_to_level(exam.level):
            has_access = True
            break
    
    if not has_access:
        messages.warning(request, 'You need to enroll to take mock exams')
        return redirect('courses:course_list')
    
    # Create new attempt
    attempt = MockExamAttempt.objects.create(
        user=request.user,
        exam=exam,
        status='IN_PROGRESS'
    )
    
    messages.success(request, 'Exam started! Good luck!')
    return redirect('exams:take_mock_exam', exam_id=exam_id, attempt_id=attempt.id)


@login_required
def take_mock_exam_view(request, exam_id, attempt_id):
    """Take the mock exam"""
    exam = get_object_or_404(MockExam, id=exam_id, is_active=True)
    attempt = get_object_or_404(MockExamAttempt, id=attempt_id, user=request.user, exam=exam)
    
    # Check if attempt is still in progress
    if attempt.status != 'IN_PROGRESS':
        messages.warning(request, 'This exam has already been completed or submitted.')
        return redirect('exams:mock_exam_detail', exam_id=exam_id)
    
    # Get all sections with their questions grouped by exercise context
    sections_data = []
    for section in exam.sections.all().prefetch_related('questions__question__options', 'questions__question__exercise_context'):
        # Group questions by exercise context
        exercises = {}
        standalone_questions = []
        
        for exam_question in section.questions.all().order_by('order_index'):
            question = exam_question.question
            
            if question.exercise_context:
                context_id = question.exercise_context.id
                if context_id not in exercises:
                    exercises[context_id] = {
                        'context': question.exercise_context,
                        'questions': []
                    }
                exercises[context_id]['questions'].append({
                    'exam_question': exam_question,
                    'question': question
                })
            else:
                standalone_questions.append({
                    'exam_question': exam_question,
                    'question': question
                })
        
        # Sort exercises by order_index
        sorted_exercises = sorted(exercises.values(), key=lambda x: x['context'].order_index)
        
        sections_data.append({
            'section': section,
            'exercises': sorted_exercises,
            'standalone_questions': standalone_questions
        })
    
    context = {
        'exam': exam,
        'attempt': attempt,
        'sections_data': sections_data
    }
    return render(request, 'exams/take_mock_exam.html', context)



@login_required
def submit_mock_exam_view(request, exam_id, attempt_id):
    """Submit the mock exam"""
    exam = get_object_or_404(MockExam, id=exam_id, is_active=True)
    attempt = get_object_or_404(MockExamAttempt, id=attempt_id, user=request.user, exam=exam)
    
    if attempt.status != 'IN_PROGRESS':
        messages.warning(request, 'This exam has already been submitted.')
        return redirect('exams:mock_exam_detail', exam_id=exam_id)
    
    if request.method == 'POST':
        # Process all submissions
        total_score = 0
        listening_score = 0
        reading_score = 0
        writing_score = 0
        speaking_score = 0
        
        sections = exam.sections.all()
        
        for section in sections:
            section_score = 0
            section_max = 0
            
            for exam_question in section.questions.all():
                question = exam_question.question
                section_max += float(question.marks)
                
                # Create or get submission
                submission, created = Submission.objects.get_or_create(
                    user=request.user,
                    question=question,
                    defaults={'max_score': question.marks}
                )
                
                # Handle different question types
                if question.question_type in ['MCQ_SINGLE', 'MCQ_MULTIPLE', 'TRUE_FALSE', 'MATCHING']:
                    selected_option_ids = request.POST.getlist(f'question_{question.id}') or [request.POST.get(f'question_{question.id}')]
                    selected_option_ids = [id for id in selected_option_ids if id]
                    
                    if selected_option_ids:
                        selected_options = Option.objects.filter(id__in=selected_option_ids)
                        submission.selected_options.set(selected_options)
                        
                        correct_options = question.options.filter(is_correct=True)
                        if correct_options.count() == selected_options.count() and \
                           all(opt.is_correct for opt in selected_options):
                            submission.score = question.marks
                            section_score += float(question.marks)
                        else:
                            submission.score = 0
                    else:
                        submission.score = 0
                    
                    submission.review_status = 'AUTO_GRADED'
                
                elif question.question_type in ['FILL_BLANK', 'INFORMATION_EXTRACTION', 'YES_NO_NOT_MENTIONED']:
                    answer = request.POST.get(f'question_{question.id}', '')
                    submission.answer_text = answer
                    submission.review_status = 'PENDING'
                    submission.score = 0  # Will be graded manually
                
                elif question.question_type in ['EMAIL_WRITING', 'SHORT_PARAGRAPH', 'OPINION_TEXT']:
                    answer = request.POST.get(f'question_{question.id}', '')
                    submission.answer_text = answer
                    submission.review_status = 'PENDING'
                    submission.score = 0  # Will be graded manually
                
                elif question.question_type in ['ROLE_PLAY', 'IMAGE_DESCRIPTION', 'TOPIC_MONOLOGUE']:
                    if f'question_{question.id}_file' in request.FILES:
                        submission.file_upload = request.FILES[f'question_{question.id}_file']
                    submission.review_status = 'PENDING'
                    submission.score = 0  # Will be graded manually
                
                submission.save()
            
            # Update section scores
            if section.category.name == 'LISTENING':
                listening_score = section_score
            elif section.category.name == 'READING':
                reading_score = section_score
            elif section.category.name == 'WRITING':
                writing_score = section_score
            elif section.category.name == 'SPEAKING':
                speaking_score = section_score
            
            total_score += section_score
        
        # Update attempt
        from django.utils import timezone
        attempt.status = 'SUBMITTED'
        attempt.submitted_at = timezone.now()
        attempt.total_score = total_score
        attempt.listening_score = listening_score
        attempt.reading_score = reading_score
        attempt.writing_score = writing_score
        attempt.speaking_score = speaking_score
        attempt.save()
        
        messages.success(request, f'Exam submitted successfully! Total Score: {total_score}/{exam.total_marks}')
        return redirect('exams:mock_exam_result', exam_id=exam_id, attempt_id=attempt_id)
    
    return redirect('exams:take_mock_exam', exam_id=exam_id, attempt_id=attempt_id)


@login_required
def mock_exam_result_view(request, exam_id, attempt_id):
    """View mock exam results"""
    exam = get_object_or_404(MockExam, id=exam_id)
    attempt = get_object_or_404(MockExamAttempt, id=attempt_id, user=request.user, exam=exam)
    
    context = {
        'exam': exam,
        'attempt': attempt
    }
    return render(request, 'exams/mock_exam_result.html', context)
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import uuid

from .models import (
    Question, Option, Submission, MockExam, MockExamAttempt, 
    MockExamSection, MockExamQuestion, MockExamPackage, 
    MockExamPurchase, MockExamAccess
)
from courses.models import VideoLesson
from enrollments.models import Enrollment


# ... (existing views remain the same) ...


def pricing_view(request):
    """Display all available mock exam packages"""
    packages = MockExamPackage.objects.filter(is_active=True).order_by('display_order', 'level')
    
    context = {
        'packages': packages
    }
    return render(request, 'exams/pricing.html', context)


@login_required
def purchase_package_view(request, package_id):
    """Handle package purchase with custom Stripe checkout"""
    import stripe
    from django.conf import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    package = get_object_or_404(MockExamPackage, id=package_id, is_active=True)
    
    # Check if user already purchased this package
    existing_purchase = MockExamPurchase.objects.filter(
        user=request.user,
        package=package,
        payment_status='completed'
    ).first()
    
    if existing_purchase:
        messages.info(request, 'You have already purchased this package!')
        return redirect('exams:my_purchases')
    
    if request.method == 'POST':
        try:
            # Create Stripe Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=int(package.price * 100),  # Convert to cents
                currency=package.currency.lower(),
                metadata={
                    'user_id': str(request.user.id),
                    'package_id': str(package.id),
                    'package_name': package.name,
                    'package_level': package.level,
                }
            )
            
            # Create pending purchase record
            purchase = MockExamPurchase.objects.create(
                user=request.user,
                package=package,
                amount_paid=package.price,
                currency=package.currency,
                transaction_id=intent.id,
                payment_status='pending',
                payment_method='stripe'
            )
            
            context = {
                'package': package,
                'purchase': purchase,
                'client_secret': intent.client_secret,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            }
            return render(request, 'exams/checkout.html', context)
            
        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
            return redirect('exams:pricing')
    
    context = {
        'package': package,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'exams/purchase_package.html', context)



@login_required
def my_purchases_view(request):
    """Display user's purchase history and exam access"""
    purchases = MockExamPurchase.objects.filter(
        user=request.user
    ).select_related('package').order_by('-purchase_date')
    
    # Get all exams user has access to
    accessible_exams = MockExamAccess.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('exam', 'granted_via_purchase__package')
    
    context = {
        'purchases': purchases,
        'accessible_exams': accessible_exams
    }
    return render(request, 'exams/my_purchases.html', context)


@login_required
def payment_success_view(request):
    """Handle successful payment redirect"""
    import stripe
    from django.conf import settings
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    transaction_id = request.GET.get('transaction_id')
    
    if transaction_id:
        try:
            # Get the purchase record
            purchase = MockExamPurchase.objects.filter(
                transaction_id=transaction_id,
                user=request.user
            ).first()
            
            if purchase:
                # Verify payment with Stripe
                intent = stripe.PaymentIntent.retrieve(transaction_id)
                
                if intent.status == 'succeeded':
                    purchase.payment_status = 'completed'
                    purchase.save()
                    purchase.grant_access()
                    
                    context = {
                        'purchase': purchase,
                        'package': purchase.package,
                        'amount': purchase.amount_paid,
                        'currency': purchase.currency,
                    }
                    return render(request, 'exams/payment_success.html', context)
                else:
                    purchase.payment_status = 'failed'
                    purchase.save()
                    messages.error(request, 'Payment verification failed.')
        except Exception as e:
            messages.error(request, 'Payment verification failed. Please contact support.')
            return redirect('exams:my_purchases')
    
    messages.warning(request, 'No payment transaction found.')
    return redirect('exams:pricing')


@csrf_exempt
def stripe_webhook_view(request):
    """Handle Stripe webhook events"""
    import stripe
    from django.conf import settings
    from django.http import HttpResponse
    from decimal import Decimal
    from accounts.models import User
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Verify webhook signature
        if settings.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        else:
            # For development without webhook secret
            event = json.loads(payload)
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle payment_intent.succeeded event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        transaction_id = payment_intent['id']
        
        try:
            # Find the purchase record
            purchase = MockExamPurchase.objects.filter(
                transaction_id=transaction_id
            ).first()
            
            if purchase and purchase.payment_status == 'pending':
                # Update purchase status
                purchase.payment_status = 'completed'
                purchase.save()
                
                # Grant access to all exams in the package
                purchase.grant_access()
                
                print(f"✅ Purchase completed for user {purchase.user.email} - Package: {purchase.package.name}")
        except Exception as e:
            print(f"❌ Webhook error: {str(e)}")
            return HttpResponse(status=400)
    
    return HttpResponse(status=200)
