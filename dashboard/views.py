from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from enrollments.models import Enrollment, VideoProgress, ChapterProgress
from courses.models import Level, Course, VideoLesson
from exams.models import Submission, MockExamAttempt
from accounts.models import User
from .models import FAQ, FAQCategory, ContactMessage, SuccessStory, InstructorProfile, CommunityStory


def home_view(request):
    """Dashboard home - accessible to all users"""
    levels = Level.objects.filter(is_active=True).order_by('order_index')
    courses = Course.objects.filter(is_active=True).order_by('-created_at')
    faqs = FAQ.objects.filter(is_active=True)
    instructors = InstructorProfile.objects.filter(is_active=True).select_related('user')
    success_stories = SuccessStory.objects.filter(is_active=True)
    community_stories = CommunityStory.objects.filter(is_active=True)[:4]
    
    context = {
        'levels': levels,
        'courses': courses,
        'faqs': faqs,
        'instructors': instructors,
        'success_stories': success_stories,
        'community_stories': community_stories
    }
    
    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(user=request.user, status='ACTIVE')
        recent_progress = VideoProgress.objects.filter(user=request.user).order_by('-last_watched_at')[:5]
        pending_submissions = Submission.objects.filter(
            user=request.user,
            review_status='PENDING'
        ).count()
        
        context.update({
            'enrollments': enrollments,
            'recent_progress': recent_progress,
            'pending_submissions': pending_submissions
        })
    else:
        context.update({
            'enrollments': [],
            'recent_progress': [],
            'pending_submissions': 0
        })
    
    return render(request, 'dashboard/home.html', context)

def faq_list_view(request, category_slug=None):
    categories = FAQCategory.objects.filter(is_active=True)
    
    if category_slug:
        active_category = get_object_or_404(FAQCategory, slug=category_slug, is_active=True)
    else:
        active_category = categories.first()
    
    faqs = []
    if active_category:
        faqs = FAQ.objects.filter(category=active_category, is_active=True)
    
    context = {
        'categories': categories,
        'active_category': active_category,
        'faqs': faqs
    }
    return render(request, 'dashboard/faq_list.html', context)


@login_required
def my_courses_view(request):
    """User's enrolled courses with progress stats"""
    # Get course enrollments
    all_enrollments = Enrollment.objects.filter(user=request.user).select_related('course', 'course__level')
    
    # Calculate stats
    total_enrolled = all_enrollments.count()
    active = all_enrollments.filter(status='ACTIVE').count()
    completed = all_enrollments.filter(status='COMPLETED').count()
    
    # Get active enrollments
    enrollments = all_enrollments.filter(status='ACTIVE')
    
    # Enrich enrollments with progress and next video info
    for enrollment in enrollments:
        # Get the target level for progress calculation
        target_level = enrollment.level
        if not target_level and enrollment.course:
            target_level = enrollment.course.level
            
        if target_level:
            # Get all videos for the level this enrollment provides access to
            level_videos = VideoLesson.objects.filter(
                chapter__course__level=target_level,
                is_active=True
            ).order_by('chapter__order_index', 'order_index')
            total_videos = level_videos.count()
        else:
            level_videos = VideoLesson.objects.none()
            total_videos = 0
        
        if total_videos > 0:
            # Get completed videos for this user in this level
            completed_videos = VideoProgress.objects.filter(
                user=request.user,
                video__in=level_videos,
                is_completed=True
            ).values_list('video_id', flat=True)
            
            completed_count = len(completed_videos)
            enrollment.progress_percent = int((completed_count / total_videos) * 100)
            enrollment.total_videos = total_videos
            enrollment.completed_count = completed_count
            
            # Find next video: first one that is NOT completed
            next_video = level_videos.exclude(id__in=completed_videos).first()
            if not next_video:
                # If all completed, point to the first one again or stay at last
                next_video = level_videos.first()
            
            enrollment.next_video_id = next_video.id if next_video else None
        else:
            enrollment.progress_percent = 0
            enrollment.total_videos = 0
            enrollment.completed_count = 0
            enrollment.next_video_id = None
    
    # Get purchased mock exam packages
    from exams.models import MockExamPurchase
    purchased_packages = MockExamPurchase.objects.filter(
        user=request.user,
        payment_status='completed'
    ).select_related('package').order_by('-purchase_date')

    context = {
        'enrollments': enrollments,
        'purchased_packages': purchased_packages,
        'stats': {
            'total': total_enrolled,
            'active': active,
            'completed': completed
        }
    }
    return render(request, 'dashboard/my_courses.html', context)


@login_required
def profile_view(request):
    """User profile"""
    # Fetch data for statistics
    enrollments = Enrollment.objects.filter(user=request.user, status='ACTIVE')
    enrollments_count = enrollments.count()
    
    # Fetch video progress
    all_video_progress = VideoProgress.objects.filter(user=request.user)
    videos_completed = all_video_progress.filter(is_completed=True).count()
    
    # Recent activity
    recent_progress = all_video_progress.order_by('-last_watched_at')[:5]
    
    # Pending submissions for reviewer/admin context (if applicable) or for own submissions
    pending_submissions = Submission.objects.filter(
        user=request.user,
        review_status='PENDING'
    ).count()
    
    mock_exams_taken = MockExamAttempt.objects.filter(user=request.user).count()
    
    context = {
        'enrollments': enrollments,
        'enrollments_count': enrollments_count,
        'videos_completed': videos_completed,
        'mock_exams_taken': mock_exams_taken,
        'recent_progress': recent_progress,
        'pending_submissions': pending_submissions,
    }
    return render(request, 'dashboard/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile"""
    if request.method == 'POST':
        from django.contrib import messages
        
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        
        # Update user
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            profile_picture = request.FILES['profile_picture']
            
            # Validate file size (max 5MB)
            if profile_picture.size > 5 * 1024 * 1024:
                messages.error(request, 'Profile picture must be less than 5MB')
                return render(request, 'dashboard/edit_profile.html')
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/jpg', 'image/gif']
            if profile_picture.content_type not in allowed_types:
                messages.error(request, 'Profile picture must be a JPEG, PNG, or GIF image')
                return render(request, 'dashboard/edit_profile.html')
            
            user.profile_picture = profile_picture
        
        try:
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard:profile')
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            return render(request, 'dashboard/edit_profile.html')
    

def terms_view(request):
    """Terms and Service page"""
    return render(request, 'dashboard/terms.html')


def privacy_view(request):
    """Privacy Policy page"""
    return render(request, 'dashboard/privacy.html')


def contact_view(request):
    """Contact Us page with form handling"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject or "No Subject",
                message=message
            )
            messages.success(request, "Your message has been sent successfully! We will get back to you soon.")
            return redirect('dashboard:contact')
        else:
            messages.error(request, "Please fill in all required fields.")
            
    return render(request, 'dashboard/contact.html')


def instructor_list_view(request):
    """Dynamic list of instructors"""
    instructors = InstructorProfile.objects.filter(is_active=True)
    return render(request, 'dashboard/instructor_list.html', {'instructors': instructors})


def instructor_detail_view(request, pk):
    """Instructor profile detail view"""
    instructor = get_object_or_404(InstructorProfile, pk=pk, is_active=True)
    return render(request, 'dashboard/instructor_detail.html', {'instructor': instructor})


def community_story_detail_view(request, pk):
    """Community story detail view"""
    story = get_object_or_404(CommunityStory, pk=pk, is_active=True)
    return render(request, 'dashboard/community_story_detail.html', {'story': story})


def success_story_list_view(request):
    """Dynamic list of success stories"""
    stories = SuccessStory.objects.filter(is_active=True)
    return render(request, 'dashboard/success_stories.html', {'stories': stories})
