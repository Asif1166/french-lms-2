from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q

from courses.models import (
    LevelCode, Level, Category, Chapter,
    VideoLesson, LessonResource, WordMeaning, Course,
)
from accounts.models import User
from enrollments.models import Enrollment
from .decorators import admin_required
from .forms import (
    LevelCodeForm, LevelForm, CategoryForm, ChapterForm,
    VideoLessonForm, LessonResourceForm, WordMeaningForm, CourseForm,
)


# ─────────────────────────────────────────────────────────────────────────────
# Auth
# ─────────────────────────────────────────────────────────────────────────────

def admin_login(request):
    if request.user.is_authenticated and (
        request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', None) == 'ADMIN'
    ):
        return redirect('custom_admin:dashboard')

    error = None
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is None:
            error = 'Invalid email or password.'
        elif not (user.is_staff or user.is_superuser or getattr(user, 'role', None) == 'ADMIN'):
            error = 'You do not have admin access.'
        else:
            login(request, user)
            next_url = request.GET.get('next', '')
            return redirect(next_url or 'custom_admin:dashboard')

    return render(request, 'custom_admin/login.html', {'error': error})


def admin_logout(request):
    logout(request)
    return redirect('custom_admin:login')


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def dashboard(request):
    stats = {
        'total_courses': Course.objects.count(),
        'total_users': User.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
        'active_courses': Course.objects.filter(is_active=True).count(),
        'total_levels': Level.objects.count(),
        'total_chapters': Chapter.objects.count(),
        'total_videos': VideoLesson.objects.count(),
    }
    recent_courses = Course.objects.select_related('level__level_code').order_by('-created_at')[:5]
    return render(request, 'custom_admin/dashboard.html', {
        'stats': stats,
        'recent_courses': recent_courses,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Level Codes
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def level_code_list(request):
    qs = LevelCode.objects.all().order_by('code')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(code__icontains=search) | Q(name__icontains=search))
    return render(request, 'custom_admin/level_codes/list.html', {
        'level_codes': qs, 'search': search,
    })


@admin_required
def level_code_create(request):
    form = LevelCodeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Level code created successfully.')
        return redirect('custom_admin:level_code_list')
    return render(request, 'custom_admin/level_codes/form.html', {
        'form': form, 'action': 'Create', 'obj': None,
    })


@admin_required
def level_code_edit(request, pk):
    obj = get_object_or_404(LevelCode, pk=pk)
    form = LevelCodeForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Level code "{obj.code}" updated.')
        return redirect('custom_admin:level_code_list')
    return render(request, 'custom_admin/level_codes/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
    })


@admin_required
def level_code_delete(request, pk):
    obj = get_object_or_404(LevelCode, pk=pk)
    if request.method == 'POST':
        label = obj.code
        obj.delete()
        messages.success(request, f'Level code "{label}" deleted.')
        return redirect('custom_admin:level_code_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Level Code',
        'object_label': str(obj),
        'cancel_url': '/panel/level-codes/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Levels
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def level_list(request):
    qs = Level.objects.select_related('level_code').order_by('order_index', 'level_code__code')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(level_code__code__icontains=search))
    return render(request, 'custom_admin/levels/list.html', {
        'levels': qs, 'search': search,
    })


@admin_required
def level_create(request):
    form = LevelForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Level created successfully.')
        return redirect('custom_admin:level_list')
    return render(request, 'custom_admin/levels/form.html', {
        'form': form, 'action': 'Create', 'obj': None,
    })


@admin_required
def level_edit(request, pk):
    obj = get_object_or_404(Level, pk=pk)
    form = LevelForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Level "{obj.title}" updated.')
        return redirect('custom_admin:level_list')
    return render(request, 'custom_admin/levels/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
    })


@admin_required
def level_delete(request, pk):
    obj = get_object_or_404(Level, pk=pk)
    if request.method == 'POST':
        label = obj.title
        obj.delete()
        messages.success(request, f'Level "{label}" deleted.')
        return redirect('custom_admin:level_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Level',
        'object_label': str(obj),
        'cancel_url': '/panel/levels/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Categories
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def category_list(request):
    qs = Category.objects.all().order_by('order_index')
    return render(request, 'custom_admin/categories/list.html', {'categories': qs})


@admin_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category created successfully.')
        return redirect('custom_admin:category_list')
    return render(request, 'custom_admin/categories/form.html', {
        'form': form, 'action': 'Create', 'obj': None,
    })


@admin_required
def category_edit(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Category "{obj.get_name_display()}" updated.')
        return redirect('custom_admin:category_list')
    return render(request, 'custom_admin/categories/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
    })


@admin_required
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        label = obj.get_name_display()
        obj.delete()
        messages.success(request, f'Category "{label}" deleted.')
        return redirect('custom_admin:category_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Category',
        'object_label': str(obj),
        'cancel_url': '/panel/categories/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Chapters
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def chapter_list(request):
    qs = Chapter.objects.select_related('level__level_code').order_by('level__level_code__code', 'order_index')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(level__title__icontains=search))
    level_filter = request.GET.get('level', '').strip()
    if level_filter:
        qs = qs.filter(level_id=level_filter)
    levels = Level.objects.select_related('level_code').order_by('order_index')
    return render(request, 'custom_admin/chapters/list.html', {
        'chapters': qs, 'search': search,
        'levels': levels, 'level_filter': level_filter,
    })


@admin_required
def chapter_create(request):
    form = ChapterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Chapter created successfully.')
        return redirect('custom_admin:chapter_list')
    return render(request, 'custom_admin/chapters/form.html', {
        'form': form, 'action': 'Create', 'obj': None,
    })


@admin_required
def chapter_edit(request, pk):
    obj = get_object_or_404(Chapter, pk=pk)
    form = ChapterForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Chapter "{obj.title}" updated.')
        return redirect('custom_admin:chapter_list')
    return render(request, 'custom_admin/chapters/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
    })


@admin_required
def chapter_delete(request, pk):
    obj = get_object_or_404(Chapter, pk=pk)
    if request.method == 'POST':
        label = obj.title
        obj.delete()
        messages.success(request, f'Chapter "{label}" deleted.')
        return redirect('custom_admin:chapter_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Chapter',
        'object_label': str(obj),
        'cancel_url': '/panel/chapters/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Video Lessons
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def video_lesson_list(request):
    qs = VideoLesson.objects.select_related(
        'chapter__level__level_code', 'category'
    ).order_by('chapter__level__level_code__code', 'chapter__order_index', 'order_index')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(chapter__title__icontains=search))
    chapter_filter = request.GET.get('chapter', '').strip()
    if chapter_filter:
        qs = qs.filter(chapter_id=chapter_filter)
    chapters = Chapter.objects.select_related('level__level_code').order_by('level__level_code__code', 'order_index')
    return render(request, 'custom_admin/video_lessons/list.html', {
        'video_lessons': qs, 'search': search,
        'chapters': chapters, 'chapter_filter': chapter_filter,
    })


@admin_required
def video_lesson_create(request):
    form = VideoLessonForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        lesson = form.save()
        messages.success(request, 'Video lesson created. Now add resources and vocabulary below.')
        return redirect('custom_admin:video_lesson_edit', pk=lesson.pk)
    return render(request, 'custom_admin/video_lessons/form.html', {
        'form': form, 'action': 'Create', 'obj': None,
    })


@admin_required
def video_lesson_edit(request, pk):
    obj = get_object_or_404(VideoLesson, pk=pk)
    form = VideoLessonForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Video lesson "{obj.title}" updated.')
        return redirect('custom_admin:video_lesson_list')
    return render(request, 'custom_admin/video_lessons/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
        'resources': obj.resources.all().order_by('order_index'),
        'word_meanings': obj.word_meanings.all().order_by('order_index', 'word'),
    })


@admin_required
def video_lesson_delete(request, pk):
    obj = get_object_or_404(VideoLesson, pk=pk)
    if request.method == 'POST':
        label = obj.title
        obj.delete()
        messages.success(request, f'Video lesson "{label}" deleted.')
        return redirect('custom_admin:video_lesson_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Video Lesson',
        'object_label': str(obj),
        'cancel_url': '/panel/video-lessons/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Lesson Resources
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def lesson_resource_list(request):
    qs = LessonResource.objects.select_related('video__chapter__level__level_code').order_by('video__title', 'order_index')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(video__title__icontains=search))
    video_filter = request.GET.get('video', '').strip()
    if video_filter:
        qs = qs.filter(video_id=video_filter)
    videos = VideoLesson.objects.select_related('chapter__level__level_code').order_by('chapter__level__level_code__code', 'title')
    return render(request, 'custom_admin/lesson_resources/list.html', {
        'resources': qs, 'search': search,
        'videos': videos, 'video_filter': video_filter,
    })


@admin_required
def lesson_resource_create(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    video_id = request.GET.get('video') or request.POST.get('_video_id') or ''
    initial = {}
    if video_id:
        try:
            initial['video'] = int(video_id)
        except (ValueError, TypeError):
            video_id = ''

    form = LessonResourceForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            resource = form.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'id': resource.pk,
                    'title': resource.title,
                    'resource_type': resource.resource_type,
                    'file_url': resource.file.url,
                    'order_index': resource.order_index,
                    'edit_url': reverse('custom_admin:lesson_resource_edit', args=[resource.pk]),
                    'delete_url': reverse('custom_admin:lesson_resource_delete', args=[resource.pk]),
                })
            messages.success(request, 'Lesson resource created successfully.')
            if video_id:
                return redirect('custom_admin:video_lesson_edit', pk=int(video_id))
            return redirect('custom_admin:lesson_resource_list')
        elif is_ajax:
            return JsonResponse({'success': False, 'errors': {k: list(v) for k, v in form.errors.items()}})

    return render(request, 'custom_admin/lesson_resources/form.html', {
        'form': form, 'action': 'Create', 'obj': None, 'video_id': video_id,
    })


@admin_required
def lesson_resource_edit(request, pk):
    obj = get_object_or_404(LessonResource, pk=pk)
    video_pk = obj.video.pk
    form = LessonResourceForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Resource "{obj.title}" updated.')
        return redirect('custom_admin:video_lesson_edit', pk=video_pk)
    return render(request, 'custom_admin/lesson_resources/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj, 'video_id': str(video_pk),
    })


@admin_required
def lesson_resource_delete(request, pk):
    obj = get_object_or_404(LessonResource, pk=pk)
    video_pk = obj.video.pk
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        label = obj.title
        obj.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        messages.success(request, f'Resource "{label}" deleted.')
        return redirect('custom_admin:video_lesson_edit', pk=video_pk)
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Lesson Resource',
        'object_label': str(obj),
        'cancel_url': f'/panel/video-lessons/{video_pk}/edit/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Word Meanings
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def word_meaning_list(request):
    qs = WordMeaning.objects.select_related('video__chapter__level__level_code').order_by('video__title', 'order_index', 'word')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(word__icontains=search) | Q(video__title__icontains=search))
    video_filter = request.GET.get('video', '').strip()
    if video_filter:
        qs = qs.filter(video_id=video_filter)
    videos = VideoLesson.objects.select_related('chapter__level__level_code').order_by('chapter__level__level_code__code', 'title')
    return render(request, 'custom_admin/word_meanings/list.html', {
        'word_meanings': qs, 'search': search,
        'videos': videos, 'video_filter': video_filter,
    })


@admin_required
def word_meaning_create(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    video_id = request.GET.get('video') or request.POST.get('_video_id') or ''
    initial = {}
    if video_id:
        try:
            initial['video'] = int(video_id)
        except (ValueError, TypeError):
            video_id = ''

    form = WordMeaningForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            wm = form.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'id': wm.pk,
                    'word': wm.word,
                    'ipa_pronunciation': wm.ipa_pronunciation or '',
                    'meaning': wm.meaning,
                    'audio_url': wm.audio_file.url if wm.audio_file else '',
                    'order_index': wm.order_index,
                    'edit_url': reverse('custom_admin:word_meaning_edit', args=[wm.pk]),
                    'delete_url': reverse('custom_admin:word_meaning_delete', args=[wm.pk]),
                })
            messages.success(request, 'Word meaning created successfully.')
            if video_id:
                return redirect('custom_admin:video_lesson_edit', pk=int(video_id))
            return redirect('custom_admin:word_meaning_list')
        elif is_ajax:
            return JsonResponse({'success': False, 'errors': {k: list(v) for k, v in form.errors.items()}})

    return render(request, 'custom_admin/word_meanings/form.html', {
        'form': form, 'action': 'Create', 'obj': None, 'video_id': video_id,
    })


@admin_required
def word_meaning_edit(request, pk):
    obj = get_object_or_404(WordMeaning, pk=pk)
    video_pk = obj.video.pk
    form = WordMeaningForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Word "{obj.word}" updated.')
        return redirect('custom_admin:video_lesson_edit', pk=video_pk)
    return render(request, 'custom_admin/word_meanings/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj, 'video_id': str(video_pk),
    })


@admin_required
def word_meaning_delete(request, pk):
    obj = get_object_or_404(WordMeaning, pk=pk)
    video_pk = obj.video.pk
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        label = obj.word
        obj.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        messages.success(request, f'Word "{label}" deleted.')
        return redirect('custom_admin:video_lesson_edit', pk=video_pk)
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Word Meaning',
        'object_label': str(obj),
        'cancel_url': f'/panel/video-lessons/{video_pk}/edit/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Courses
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def course_list(request):
    courses = Course.objects.select_related('level__level_code').order_by('-created_at')
    search = request.GET.get('q', '').strip()
    if search:
        courses = courses.filter(name__icontains=search)
    return render(request, 'custom_admin/courses/list.html', {
        'courses': courses, 'search': search,
    })


@admin_required
def course_create(request):
    form = CourseForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Course created successfully!')
        return redirect('custom_admin:course_list')
    return render(request, 'custom_admin/courses/form.html', {
        'form': form, 'action': 'Create', 'obj': None,
    })


@admin_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, request.FILES or None, instance=course)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Course "{course.name}" updated successfully!')
        return redirect('custom_admin:course_list')
    return render(request, 'custom_admin/courses/form.html', {
        'form': form, 'action': 'Edit', 'obj': course,
    })


@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        name = course.name
        course.delete()
        messages.success(request, f'Course "{name}" deleted successfully!')
        return redirect('custom_admin:course_list')
    return render(request, 'custom_admin/courses/delete.html', {'course': course})
