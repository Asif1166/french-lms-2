from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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
        form.save()
        messages.success(request, 'Video lesson created successfully.')
        return redirect('custom_admin:video_lesson_list')
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
    form = LessonResourceForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Lesson resource created successfully.')
        return redirect('custom_admin:lesson_resource_list')
    return render(request, 'custom_admin/lesson_resources/form.html', {
        'form': form, 'action': 'Create', 'obj': None,
    })


@admin_required
def lesson_resource_edit(request, pk):
    obj = get_object_or_404(LessonResource, pk=pk)
    form = LessonResourceForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Resource "{obj.title}" updated.')
        return redirect('custom_admin:lesson_resource_list')
    return render(request, 'custom_admin/lesson_resources/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
    })


@admin_required
def lesson_resource_delete(request, pk):
    obj = get_object_or_404(LessonResource, pk=pk)
    if request.method == 'POST':
        label = obj.title
        obj.delete()
        messages.success(request, f'Resource "{label}" deleted.')
        return redirect('custom_admin:lesson_resource_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Lesson Resource',
        'object_label': str(obj),
        'cancel_url': '/panel/lesson-resources/',
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
    form = WordMeaningForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Word meaning created successfully.')
        return redirect('custom_admin:word_meaning_list')
    return render(request, 'custom_admin/word_meanings/form.html', {
        'form': form, 'action': 'Create', 'obj': None,
    })


@admin_required
def word_meaning_edit(request, pk):
    obj = get_object_or_404(WordMeaning, pk=pk)
    form = WordMeaningForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Word "{obj.word}" updated.')
        return redirect('custom_admin:word_meaning_list')
    return render(request, 'custom_admin/word_meanings/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
    })


@admin_required
def word_meaning_delete(request, pk):
    obj = get_object_or_404(WordMeaning, pk=pk)
    if request.method == 'POST':
        label = obj.word
        obj.delete()
        messages.success(request, f'Word "{label}" deleted.')
        return redirect('custom_admin:word_meaning_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Word Meaning',
        'object_label': str(obj),
        'cancel_url': '/panel/word-meanings/',
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
        'form': form, 'action': 'Create', 'course': None,
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
        'form': form, 'action': 'Edit', 'course': course,
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
