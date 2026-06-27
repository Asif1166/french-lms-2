from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Prefetch
from .models import Level, Chapter, VideoLesson, Course
from enrollments.models import Enrollment, VideoProgress, ChapterProgress


def level_list_view(request):
    """Display all CEFR levels and available courses"""
    levels = Level.objects.filter(is_active=True).order_by('order_index')
    courses = Course.objects.filter(is_active=True).order_by('-created_at')
    context = {
        'levels': levels,
        'courses': courses
    }
    return render(request, 'courses/level_list.html', context)


def level_detail_view(request, level_id):
    """Display chapters for a specific level"""
    level = get_object_or_404(Level, id=level_id, is_active=True)
    chapters = level.chapters.filter(is_active=True).order_by('order_index')
    
    # Check enrollment if user is authenticated
    has_access = False
    if request.user.is_authenticated:
        enrollments = Enrollment.objects.filter(
            user=request.user,
            status='ACTIVE'
        )
        for enrollment in enrollments:
            if enrollment.has_access_to_level(level):
                has_access = True
                break
    
    context = {
        'level': level,
        'chapters': chapters,
        'has_access': has_access
    }
    return render(request, 'courses/level_detail.html', context)


@login_required
def chapter_detail_view(request, chapter_id):
    """Display videos for a specific chapter"""
    chapter = get_object_or_404(Chapter, id=chapter_id, is_active=True)
    videos = chapter.videos.filter(is_active=True).order_by('order_index')
    
    # Check enrollment
    has_access = False
    enrollments = Enrollment.objects.filter(
        user=request.user,
        status='ACTIVE'
    )
    for enrollment in enrollments:
        if enrollment.has_access_to_level(chapter.course.level):
            has_access = True
            break

    if not has_access:
        messages.warning(request, 'You need to enroll in this course to access content')
        return redirect('courses:level_detail', level_id=chapter.course.level.id)
    
    # Get progress
    chapter_progress, _ = ChapterProgress.objects.get_or_create(
        user=request.user,
        chapter=chapter
    )
    
    # Get completed video IDs
    completed_video_ids = VideoProgress.objects.filter(
        user=request.user,
        video__chapter=chapter,
        is_completed=True
    ).values_list('video_id', flat=True)
    
    context = {
        'chapter': chapter,
        'videos': videos,
        'chapter_progress': chapter_progress,
        'completed_video_ids': set(completed_video_ids)
    }
    return render(request, 'courses/chapter_detail.html', context)


@login_required
def video_detail_view(request, video_id):
    """Display video player and questions"""
    video = get_object_or_404(VideoLesson, id=video_id, is_active=True)
    
    # Check enrollment
    has_access = False
    enrollments = Enrollment.objects.filter(
        user=request.user,
        status='ACTIVE'
    )
    for enrollment in enrollments:
        if enrollment.has_access_to_level(video.chapter.course.level):
            has_access = True
            break

    if not has_access:
        messages.warning(request, 'You need to enroll in this course to access content')
        return redirect('courses:level_detail', level_id=video.chapter.course.level.id)
    
    # Get or create video progress
    video_progress, _ = VideoProgress.objects.get_or_create(
        user=request.user,
        video=video
    )
    
    # Get questions for this video
    questions = video.questions.filter(is_active=True).order_by('order_index')
    
    # Group questions by exercise context
    from collections import defaultdict
    contexts_with_questions = []
    standalone_questions = []
    
    # Get all exercise contexts for this video
    exercise_contexts = video.exercise_contexts.all().order_by('order_index')
    
    for context in exercise_contexts:
        context_questions = questions.filter(exercise_context=context).order_by('order_index')
        if context_questions.exists():
            contexts_with_questions.append({
                'context': context,
                'questions': context_questions
            })
    
    # Get questions without context
    standalone_questions = questions.filter(exercise_context__isnull=True).order_by('order_index')
    
    # Get all chapters and videos for this level to show in sidebar
    level_chapters = video.chapter.course.chapters.filter(is_active=True).prefetch_related(
        Prefetch('videos', queryset=VideoLesson.objects.filter(is_active=True).order_by('order_index'))
    ).order_by('order_index')
    
    # Get all completed video IDs for this level
    completed_video_ids = VideoProgress.objects.filter(
        user=request.user,
        video__chapter__course=video.chapter.course,
        is_completed=True
    ).values_list('video_id', flat=True)
    
    # Get word meanings for this video
    word_meanings = video.word_meanings.all().order_by('order_index', 'word')

    context = {
        'video': video,
        'questions': questions,
        'contexts_with_questions': contexts_with_questions,
        'standalone_questions': standalone_questions,
        'word_meanings': word_meanings,
        'video_progress': video_progress,
        'level_chapters': level_chapters,
        'completed_video_ids': set(completed_video_ids)
    }
    return render(request, 'courses/video_detail.html', context)



def course_list_view(request):
    """Display all available courses"""
    courses = Course.objects.filter(is_active=True).order_by('-created_at')
    levels = Level.objects.all().order_by('id')
    context = {
        'courses': courses,
        'levels': levels
    }
    return render(request, 'courses/course_list.html', context)


def course_detail_view(request, course_id):
    """Display detailed information about a course"""
    course = get_object_or_404(Course, id=course_id, is_active=True)
    
    # Check if already enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user, 
            course=course, 
            status='ACTIVE'
        ).exists()
    
    # Calculate stats dynamically
    total_videos = 0
    total_exercises = 0
    if course.is_full_access and course.level:
        chapters = Chapter.objects.filter(course__level=course.level, is_active=True).prefetch_related('videos__questions').order_by('order_index')
    else:
        chapters = course.chapters.filter(is_active=True).prefetch_related('videos__questions').order_by('order_index')
    for chapter in chapters:
        videos = chapter.videos.all()
        total_videos += videos.count()
        for video in videos:
            total_exercises += video.questions.count()
    
    total_mock_exams = 0
    mock_exams = []
    if course.level:
        mock_exams = course.level.mock_exams.filter(is_active=True).order_by('id')
        total_mock_exams = mock_exams.count()
    
    context = {
        'course': course,
        'chapters': chapters,
        'is_enrolled': is_enrolled,
        'mock_exams': mock_exams,
        'stats': {
            'videos': total_videos,
            'exercises': total_exercises,
            'mock_exams': total_mock_exams
        }
    }
    return render(request, 'courses/course_detail.html', context)
