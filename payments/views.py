import stripe
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import PaymentTransaction, PaymentWebhook
from courses.models import Course, Level
from enrollments.models import Enrollment
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_enrollment_confirmation_email(request, enrollment):
    """Send a premium HTML email with invoice details after enrollment"""
    user = enrollment.user
    item = enrollment.course if enrollment.course else enrollment.level
    transaction = enrollment.payment_transaction
    
    if not user.email:
        return
        
    subject = f'Welcome to {item.name if hasattr(item, "name") else item.title}! - Enrollment Confirmed'
    from_email = settings.DEFAULT_FROM_EMAIL
    to = user.email
    
    # Context for template
    context = {
        'user': user,
        'item': item,
        'transaction': transaction,
        'site_url': f"{request.scheme}://{request.get_host()}"
    }
    
    # Render HTML and plain text versions
    html_content = render_to_string('emails/enrollment_invoice.html', context)
    text_content = strip_tags(html_content)
    
    # Create email
    email = EmailMultiAlternatives(subject, text_content, from_email, [to])
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else ''


@login_required
def create_payment_view(request, course_id):
    """Create payment intent for a course - Bypass confirmation page"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(user=request.user, course=course, status='ACTIVE').exists():
        messages.info(request, 'You are already enrolled in this course')
        return redirect('dashboard:my_courses')
    
    # Check if Stripe is configured
    stripe_secret = getattr(settings, 'STRIPE_SECRET_KEY', '')
    stripe_public = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    
    if not stripe_secret or not stripe_public:
        messages.error(request, 'Stripe is not configured. Please contact administrator.')
        return redirect('courses:course_list')
    
    # Direct Payment Logic: Default to STRIPE and initialize immediately
    try:
        # Create Stripe Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=int(course.price * 100),  # Convert to cents
            currency=course.currency.lower(),
            metadata={
                'user_id': str(request.user.id),
                'course_id': str(course.id),
                'course_name': course.name,
            }
        )
        
        # Create payment transaction
        transaction = PaymentTransaction.objects.create(
            user=request.user,
            course=course,
            gateway='STRIPE',
            transaction_id=intent.id,
            amount=course.price,
            currency=course.currency,
            status='PENDING',
            gateway_response=json.loads(str(intent))
        )
        
        context = {
            'course': course,
            'transaction': transaction,
            'client_secret': intent.client_secret,
            'stripe_public_key': stripe_public,
        }
        return render(request, 'payments/payment.html', context)
    
    except stripe.error.StripeError as e:
        messages.error(request, f'Stripe error: {str(e)}')
        return redirect('courses:course_detail', course_id=course.id)
    except Exception as e:
        import traceback
        print(f"Payment error: {str(e)}")
        print(traceback.format_exc())
        messages.error(request, f'Payment error: {str(e)}. Please try again or contact support.')
        return redirect('courses:course_detail', course_id=course.id)


@login_required
def create_level_payment_view(request, level_id):
    """Create payment intent for a full level"""
    level = get_object_or_404(Level, id=level_id, is_active=True)
    
    # Check if already enrolled in this level
    if Enrollment.objects.filter(user=request.user, level=level, status='ACTIVE').exists():
        messages.info(request, f'You are already enrolled in {level.code} full access')
        return redirect('dashboard:my_courses')
    
    # Check if Stripe is configured
    stripe_secret = getattr(settings, 'STRIPE_SECRET_KEY', '')
    stripe_public = getattr(settings, 'STRIPE_PUBLIC_KEY', '')
    
    if not stripe_secret or not stripe_public:
        messages.error(request, 'Stripe is not configured. Please contact administrator.')
        return redirect('courses:level_list')
    
    price = level.discounted_price if level.discounted_price else level.price
    
    try:
        # Create Stripe Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=int(price * 100),  # Convert to cents
            currency=level.currency.lower(),
            metadata={
                'user_id': str(request.user.id),
                'level_id': str(level.id),
                'level_code': level.code,
            }
        )
        
        # Create payment transaction
        transaction = PaymentTransaction.objects.create(
            user=request.user,
            level=level,
            gateway='STRIPE',
            transaction_id=intent.id,
            amount=price,
            currency=level.currency,
            status='PENDING',
            gateway_response=json.loads(str(intent))
        )
        
        context = {
            'level': level,
            'item_name': f"{level.code} - {level.title} (Full Access)",
            'transaction': transaction,
            'client_secret': intent.client_secret,
            'stripe_public_key': stripe_public,
        }
        return render(request, 'payments/payment.html', context)
    
    except stripe.error.StripeError as e:
        messages.error(request, f'Stripe error: {str(e)}')
        return redirect('courses:level_detail', level_id=level.id)
    except Exception as e:
        messages.error(request, f'Payment error: {str(e)}. Please try again or contact support.')
        return redirect('courses:level_detail', level_id=level.id)


@login_required
def payment_success_view(request):
    """Handle successful payment"""
    transaction_id = request.GET.get('transaction_id')
    
    if transaction_id:
        transaction = PaymentTransaction.objects.filter(
            transaction_id=transaction_id,
            user=request.user
        ).first()
        
        if transaction:
            # Verify payment with Stripe
            if transaction.gateway == 'STRIPE' and stripe.api_key:
                try:
                    intent = stripe.PaymentIntent.retrieve(transaction.transaction_id)
                    
                    if intent.status == 'succeeded':
                        transaction.status = 'SUCCESS'
                        transaction.gateway_response = json.loads(str(intent))
                        transaction.save()
                        
                        # Create enrollment
                        enrollment_kwargs = {
                            'user': request.user,
                            'payment_transaction': transaction,
                            'status': 'ACTIVE'
                        }
                        if transaction.course:
                            enrollment_kwargs['course'] = transaction.course
                        else:
                            enrollment_kwargs['level'] = transaction.level
                            
                        enrollment, created = Enrollment.objects.get_or_create(
                            user=request.user,
                            course=transaction.course,
                            level=transaction.level,
                            defaults={
                                'payment_transaction': transaction,
                                'status': 'ACTIVE'
                            }
                        )
                        
                        if created:
                            item_name = transaction.course.name if transaction.course else transaction.level.title
                            messages.success(request, f'Successfully enrolled in {item_name}!')
                            # Send confirmation email
                            send_enrollment_confirmation_email(request, enrollment)
                        else:
                            messages.info(request, 'You are already enrolled in this course')
                        
                        return redirect('dashboard:my_courses')
                    else:
                        transaction.status = 'FAILED'
                        transaction.failure_reason = f'Payment status: {intent.status}'
                        transaction.save()
                        messages.error(request, 'Payment verification failed')
                except Exception as e:
                    messages.error(request, f'Payment verification error: {str(e)}')
    
    return redirect('courses:course_list')


@login_required
def payment_cancel_view(request):
    """Handle cancelled payment"""
    messages.info(request, 'Payment was cancelled')
    return redirect('courses:course_list')


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook_view(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET if hasattr(settings, 'STRIPE_WEBHOOK_SECRET') else ''
    
    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        else:
            # For development, parse without verification
            event = json.loads(payload)
        
        # Store webhook
        PaymentWebhook.objects.create(
            gateway='STRIPE',
            event_type=event.get('type', 'unknown'),
            transaction_id=event.get('data', {}).get('object', {}).get('id', ''),
            payload=event
        )
        
        # Handle payment_intent.succeeded
        if event.get('type') == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            transaction_id = payment_intent['id']
            
            transaction = PaymentTransaction.objects.filter(
                transaction_id=transaction_id
            ).first()
            
            if transaction and transaction.status == 'PENDING':
                transaction.status = 'SUCCESS'
                transaction.gateway_response = payment_intent
                transaction.save()
                
                # Create enrollment
                enrollment, created = Enrollment.objects.get_or_create(
                    user=transaction.user,
                    course=transaction.course,
                    level=transaction.level,
                    defaults={
                        'payment_transaction': transaction,
                        'status': 'ACTIVE'
                    }
                )
                
                if created:
                    # Send confirmation email
                    send_enrollment_confirmation_email(request, enrollment)
        
        return HttpResponse(status=200)
    
    except ValueError as e:
        return HttpResponse(status=400)
    except Exception as e:
        return HttpResponse(status=500)
