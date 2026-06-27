from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.urls import reverse
from django.db.models import Q

from courses.models import (
    LevelCode, Level, Chapter,
    VideoLesson, LessonResource, WordMeaning, Course,
)
from exams.models import (
    ExerciseContext, Question, Option,
    MockExam, MockExamPackage, PackageFeature, MockExamSection, MockExamQuestion,
    MockExamAttempt, MockExamPurchase, Submission,
)
from payments.models import PaymentTransaction
from accounts.models import User
from enrollments.models import Enrollment
from .decorators import admin_required
from .forms import (
    LevelCodeForm, LevelForm, ChapterForm,
    VideoLessonForm, LessonResourceForm, WordMeaningForm, CourseForm,
    ExerciseContextForm, QuestionForm, OptionForm,
    MockExamForm, MockExamPackageForm, PackageFeatureForm, MockExamSectionForm,
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
# Chapters
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def chapter_list(request):
    qs = Chapter.objects.select_related('course').order_by('course__name', 'order_index')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(course__name__icontains=search))
    course_filter = request.GET.get('course', '').strip()
    if course_filter:
        qs = qs.filter(course_id=course_filter)
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/chapters/list.html', {
        'chapters': qs, 'search': search,
        'courses': courses, 'course_filter': course_filter,
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
        'chapter__course'
    ).order_by('chapter__course__level__level_code__code', 'chapter__order_index', 'order_index')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(chapter__title__icontains=search))
    chapter_filter = request.GET.get('chapter', '').strip()
    if chapter_filter:
        qs = qs.filter(chapter_id=chapter_filter)
    chapters = Chapter.objects.select_related('course').order_by('course__name', 'order_index')
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
    exercises = obj.exercise_contexts.prefetch_related('questions__options').order_by('order_index')
    return render(request, 'custom_admin/video_lessons/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
        'resources': obj.resources.all().order_by('order_index'),
        'word_meanings': obj.word_meanings.all().order_by('order_index', 'word'),
        'exercises': exercises,
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
    qs = LessonResource.objects.select_related('video__chapter__course').order_by('video__title', 'order_index')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(video__title__icontains=search))
    video_filter = request.GET.get('video', '').strip()
    if video_filter:
        qs = qs.filter(video_id=video_filter)
    videos = VideoLesson.objects.select_related('chapter__course__level__level_code').order_by('chapter__course__level__level_code__code', 'title')
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
    qs = WordMeaning.objects.select_related('video__chapter__course').order_by('video__title', 'order_index', 'word')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(word__icontains=search) | Q(video__title__icontains=search))
    video_filter = request.GET.get('video', '').strip()
    if video_filter:
        qs = qs.filter(video_id=video_filter)
    videos = VideoLesson.objects.select_related('chapter__course__level__level_code').order_by('chapter__course__level__level_code__code', 'title')
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


# ─────────────────────────────────────────────────────────────────────────────
# Exercise Contexts
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def exercise_context_create(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    video_id = request.GET.get('video') or request.POST.get('_video_id') or ''
    initial = {}
    if video_id:
        try:
            initial['video'] = int(video_id)
        except (ValueError, TypeError):
            video_id = ''

    form = ExerciseContextForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            ctx = form.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'id': ctx.pk,
                    'label': ctx.label,
                    'title': ctx.title or '',
                    'question_count': 0,
                    'total_points': str(ctx.total_points) if ctx.total_points else '',
                    'order_index': ctx.order_index,
                    'edit_url': reverse('custom_admin:exercise_context_edit', args=[ctx.pk]),
                    'delete_url': reverse('custom_admin:exercise_context_delete', args=[ctx.pk]),
                })
            messages.success(request, 'Exercise created successfully.')
            if video_id:
                return redirect('custom_admin:video_lesson_edit', pk=int(video_id))
            return redirect('custom_admin:video_lesson_list')
        elif is_ajax:
            return JsonResponse({'success': False, 'errors': {k: list(v) for k, v in form.errors.items()}})

    return render(request, 'custom_admin/exercises/context_form.html', {
        'form': form, 'action': 'Create', 'obj': None, 'video_id': video_id,
    })


@admin_required
def exercise_context_edit(request, pk):
    obj = get_object_or_404(ExerciseContext, pk=pk)
    video_pk = obj.video.pk if obj.video else None
    form = ExerciseContextForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Exercise "{obj.label}" updated.')
        if video_pk:
            return redirect('custom_admin:video_lesson_edit', pk=video_pk)
        return redirect('custom_admin:video_lesson_list')
    questions = obj.questions.prefetch_related('options').order_by('order_index')
    return render(request, 'custom_admin/exercises/context_form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
        'video_id': str(video_pk) if video_pk else '',
        'questions': questions,
    })


@admin_required
def exercise_context_delete(request, pk):
    obj = get_object_or_404(ExerciseContext, pk=pk)
    video_pk = obj.video.pk if obj.video else None
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        label = obj.label
        obj.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        messages.success(request, f'Exercise "{label}" deleted.')
        if video_pk:
            return redirect('custom_admin:video_lesson_edit', pk=video_pk)
        return redirect('custom_admin:video_lesson_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Exercise',
        'object_label': str(obj),
        'cancel_url': f'/panel/video-lessons/{video_pk}/edit/' if video_pk else '/panel/video-lessons/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Questions
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def question_create(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    ctx_id = request.GET.get('exercise_context') or request.POST.get('_ctx_id') or ''
    initial = {}
    if ctx_id:
        try:
            ctx = ExerciseContext.objects.get(pk=int(ctx_id))
            initial['exercise_context'] = ctx.pk
            initial['video'] = ctx.video_id
        except (ValueError, TypeError, ExerciseContext.DoesNotExist):
            ctx_id = ''

    form = QuestionForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            q = form.save()
            _ensure_predefined_options(q)
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'id': q.pk,
                    'question_type': q.question_type,
                    'question_type_display': q.get_question_type_display(),
                    'text': q.text,
                    'marks': str(q.marks),
                    'order_index': q.order_index,
                    'option_count': q.options.count(),
                    'edit_url': reverse('custom_admin:question_edit', args=[q.pk]),
                    'delete_url': reverse('custom_admin:question_delete', args=[q.pk]),
                })
            messages.success(request, 'Question created successfully.')
            if ctx_id:
                return redirect('custom_admin:exercise_context_edit', pk=int(ctx_id))
            return redirect('custom_admin:video_lesson_list')
        elif is_ajax:
            return JsonResponse({'success': False, 'errors': {k: list(v) for k, v in form.errors.items()}})

    return render(request, 'custom_admin/exercises/question_form.html', {
        'form': form, 'action': 'Create', 'obj': None, 'ctx_id': ctx_id,
    })


@admin_required
def question_edit(request, pk):
    obj = get_object_or_404(Question, pk=pk)
    ctx_pk = obj.exercise_context_id
    form = QuestionForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Question updated.')
        if ctx_pk:
            return redirect('custom_admin:exercise_context_edit', pk=ctx_pk)
        return redirect('custom_admin:video_lesson_list')
    options = obj.options.order_by('order_index')
    return render(request, 'custom_admin/exercises/question_form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
        'ctx_id': str(ctx_pk) if ctx_pk else '',
        'options': options,
    })


@admin_required
def question_delete(request, pk):
    obj = get_object_or_404(Question, pk=pk)
    ctx_pk = obj.exercise_context_id
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        obj.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        messages.success(request, 'Question deleted.')
        if ctx_pk:
            return redirect('custom_admin:exercise_context_edit', pk=ctx_pk)
        return redirect('custom_admin:video_lesson_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Question',
        'object_label': str(obj),
        'cancel_url': f'/panel/exercises/{ctx_pk}/edit/' if ctx_pk else '/panel/video-lessons/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Options
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def option_create(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    q_id = request.GET.get('question') or request.POST.get('_q_id') or ''
    initial = {}
    if q_id:
        try:
            initial['question'] = int(q_id)
        except (ValueError, TypeError):
            q_id = ''

    form = OptionForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            opt = form.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'id': opt.pk,
                    'text': opt.text or '',
                    'is_correct': opt.is_correct,
                    'order_index': opt.order_index,
                    'file_url': opt.file.url if opt.file else '',
                    'delete_url': reverse('custom_admin:option_delete', args=[opt.pk]),
                })
            messages.success(request, 'Option added.')
            if q_id:
                return redirect('custom_admin:question_edit', pk=int(q_id))
            return redirect('custom_admin:video_lesson_list')
        elif is_ajax:
            return JsonResponse({'success': False, 'errors': {k: list(v) for k, v in form.errors.items()}})

    return redirect('custom_admin:video_lesson_list')


@admin_required
def option_delete(request, pk):
    obj = get_object_or_404(Option, pk=pk)
    q_pk = obj.question_id
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        obj.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        messages.success(request, 'Option deleted.')
        if q_pk:
            return redirect('custom_admin:question_edit', pk=q_pk)
        return redirect('custom_admin:video_lesson_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Option',
        'object_label': str(obj),
        'cancel_url': f'/panel/questions/{q_pk}/edit/' if q_pk else '/panel/video-lessons/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Mock Exams
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def mock_exam_list(request):
    qs = MockExam.objects.select_related('level__level_code', 'package').order_by('level__level_code__code', '-created_at')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(level__level_code__code__icontains=search))
    level_filter = request.GET.get('level', '').strip()
    if level_filter:
        qs = qs.filter(level_id=level_filter)
    levels = Level.objects.select_related('level_code').order_by('order_index')
    return render(request, 'custom_admin/mock_exams/list.html', {
        'mock_exams': qs, 'search': search,
        'levels': levels, 'level_filter': level_filter,
    })


@admin_required
def mock_exam_create(request):
    form = MockExamForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        exam = form.save()
        messages.success(request, 'Mock exam created. Add sections below.')
        return redirect('custom_admin:mock_exam_edit', pk=exam.pk)
    return render(request, 'custom_admin/mock_exams/form.html', {
        'form': form, 'action': 'Create', 'obj': None,
    })


@admin_required
def mock_exam_edit(request, pk):
    obj = get_object_or_404(MockExam, pk=pk)
    form = MockExamForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Mock exam "{obj.title}" updated.')
        return redirect('custom_admin:mock_exam_list')
    sections = obj.sections.order_by('order_index')
    return render(request, 'custom_admin/mock_exams/form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
        'sections': sections,
    })


@admin_required
def mock_exam_delete(request, pk):
    obj = get_object_or_404(MockExam, pk=pk)
    if request.method == 'POST':
        label = obj.title
        obj.delete()
        messages.success(request, f'Mock exam "{label}" deleted.')
        return redirect('custom_admin:mock_exam_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Mock Exam',
        'object_label': str(obj),
        'cancel_url': '/panel/mock-exams/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Mock Exam Sections
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def mock_exam_section_create(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    exam_id = request.GET.get('exam') or request.POST.get('_exam_id') or ''
    initial = {}
    if exam_id:
        try:
            initial['exam'] = int(exam_id)
        except (ValueError, TypeError):
            exam_id = ''

    form = MockExamSectionForm(request.POST or None, initial=initial)
    if request.method == 'POST':
        if form.is_valid():
            sec = form.save()
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'id': sec.pk,
                    'title': sec.title,
                    'description': sec.description or '',
                    'duration_minutes': sec.duration_minutes,
                    'marks': str(sec.marks),
                    'order_index': sec.order_index,
                    'question_count': 0,
                    'edit_url': reverse('custom_admin:mock_exam_section_edit', args=[sec.pk]),
                    'delete_url': reverse('custom_admin:mock_exam_section_delete', args=[sec.pk]),
                })
            messages.success(request, 'Section created.')
            if exam_id:
                return redirect('custom_admin:mock_exam_edit', pk=int(exam_id))
            return redirect('custom_admin:mock_exam_list')
        elif is_ajax:
            return JsonResponse({'success': False, 'errors': {k: list(v) for k, v in form.errors.items()}})

    return redirect('custom_admin:mock_exam_list')


@admin_required
def mock_exam_section_edit(request, pk):
    obj = get_object_or_404(MockExamSection, pk=pk)
    exam_pk = obj.exam.pk
    form = MockExamSectionForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Section "{obj.title}" updated.')
        return redirect('custom_admin:mock_exam_edit', pk=exam_pk)
    section_questions = obj.questions.select_related('question').prefetch_related('question__options').order_by('order_index')
    return render(request, 'custom_admin/mock_exams/section_form.html', {
        'form': form, 'action': 'Edit', 'obj': obj, 'exam_id': str(exam_pk),
        'section_questions': section_questions,
    })


@admin_required
def mock_exam_section_delete(request, pk):
    obj = get_object_or_404(MockExamSection, pk=pk)
    exam_pk = obj.exam.pk
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        obj.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        messages.success(request, 'Section deleted.')
        return redirect('custom_admin:mock_exam_edit', pk=exam_pk)
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Mock Exam Section',
        'object_label': str(obj),
        'cancel_url': f'/panel/mock-exams/{exam_pk}/edit/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Mock Exam Packages
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def mock_exam_package_list(request):
    qs = MockExamPackage.objects.prefetch_related('features', 'exams').order_by('display_order', 'level')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(level__icontains=search))
    return render(request, 'custom_admin/mock_exams/package_list.html', {
        'packages': qs, 'search': search,
    })


@admin_required
def mock_exam_package_create(request):
    form = MockExamPackageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Package created.')
        return redirect('custom_admin:mock_exam_package_list')
    features = PackageFeature.objects.all()
    return render(request, 'custom_admin/mock_exams/package_form.html', {
        'form': form, 'action': 'Create', 'obj': None, 'features': features,
    })


@admin_required
def mock_exam_package_edit(request, pk):
    obj = get_object_or_404(MockExamPackage, pk=pk)
    form = MockExamPackageForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Package "{obj.name}" updated.')
        return redirect('custom_admin:mock_exam_package_list')
    features = PackageFeature.objects.all()
    exams = obj.exams.select_related('level__level_code').order_by('level__level_code__code')
    return render(request, 'custom_admin/mock_exams/package_form.html', {
        'form': form, 'action': 'Edit', 'obj': obj,
        'features': features, 'package_exams': exams,
    })


@admin_required
def mock_exam_package_delete(request, pk):
    obj = get_object_or_404(MockExamPackage, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'Package deleted.')
        return redirect('custom_admin:mock_exam_package_list')
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Mock Exam Package',
        'object_label': str(obj),
        'cancel_url': '/panel/mock-exam-packages/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Package Features
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def package_feature_create(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    form = PackageFeatureForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        feat = form.save()
        if is_ajax:
            return JsonResponse({'success': True, 'id': feat.pk, 'name': feat.name, 'icon': feat.icon})
        messages.success(request, 'Feature created.')
        return redirect('custom_admin:mock_exam_package_list')
    elif request.method == 'POST' and is_ajax:
        return JsonResponse({'success': False, 'errors': {k: list(v) for k, v in form.errors.items()}})
    return redirect('custom_admin:mock_exam_package_list')


def _ensure_predefined_options(question):
    """Auto-create options for TRUE_FALSE and YES_NO_NOT_MENTIONED if none exist."""
    if question.options.exists():
        return
    if question.question_type == 'TRUE_FALSE':
        Option.objects.bulk_create([
            Option(question=question, text='True', is_correct=True, order_index=0),
            Option(question=question, text='False', is_correct=False, order_index=1),
        ])
    elif question.question_type == 'YES_NO_NOT_MENTIONED':
        Option.objects.bulk_create([
            Option(question=question, text='Yes', is_correct=False, order_index=0),
            Option(question=question, text='No', is_correct=False, order_index=1),
            Option(question=question, text='Not Mentioned', is_correct=False, order_index=2),
        ])


# ─────────────────────────────────────────────────────────────────────────────
# Mock Exam Questions (link Question to Section)
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def mock_exam_question_create(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    section_id = request.POST.get('section_id') or request.GET.get('section') or ''

    if request.method != 'POST':
        return redirect('custom_admin:mock_exam_list')

    section = get_object_or_404(MockExamSection, pk=int(section_id))
    q_type = request.POST.get('question_type', 'MCQ_SINGLE')
    text = request.POST.get('text', '').strip()
    instruction = request.POST.get('instruction', '').strip()
    marks = request.POST.get('marks', '1.0')
    order = request.POST.get('order_index', '0')

    if not text:
        if is_ajax:
            return JsonResponse({'success': False, 'errors': {'text': ['Question text is required.']}})
        return redirect('custom_admin:mock_exam_section_edit', pk=section.pk)

    q = Question.objects.create(
        question_type=q_type,
        text=text,
        instruction=instruction,
        marks=marks,
        order_index=int(order),
        is_active=True,
        image=request.FILES.get('image'),
    )

    meq = MockExamQuestion.objects.create(
        section=section,
        question=q,
        order_index=int(order),
    )

    opt_texts = request.POST.getlist('opt_texts[]')
    opt_corrects = request.POST.getlist('opt_corrects[]')
    for i, opt_text in enumerate(opt_texts):
        opt_text = opt_text.strip()
        opt_file = request.FILES.get(f'opt_file_{i}')
        if not opt_text and not opt_file:
            continue
        Option.objects.create(
            question=q,
            text=opt_text,
            file=opt_file,
            is_correct=(str(i) in opt_corrects),
            order_index=i,
        )

    _ensure_predefined_options(q)

    if is_ajax:
        return JsonResponse({
            'success': True,
            'id': meq.pk,
            'question_id': q.pk,
            'question_type': q.question_type,
            'question_type_display': q.get_question_type_display(),
            'text': q.text,
            'marks': str(q.marks),
            'order_index': meq.order_index,
            'option_count': q.options.count(),
            'edit_url': reverse('custom_admin:question_edit', args=[q.pk]),
            'delete_url': reverse('custom_admin:mock_exam_question_delete', args=[meq.pk]),
        })

    messages.success(request, 'Question added to section.')
    return redirect('custom_admin:mock_exam_section_edit', pk=section.pk)


@admin_required
def mock_exam_question_delete(request, pk):
    obj = get_object_or_404(MockExamQuestion, pk=pk)
    section_pk = obj.section.pk
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        q = obj.question
        obj.delete()
        if not q.mock_exam_questions.exists() and not q.exercise_context_id and not q.video_id:
            q.delete()
        if is_ajax:
            return JsonResponse({'success': True})
        messages.success(request, 'Question removed from section.')
        return redirect('custom_admin:mock_exam_section_edit', pk=section_pk)
    return render(request, 'custom_admin/confirm_delete.html', {
        'object_type': 'Question',
        'object_label': str(obj),
        'cancel_url': f'/panel/mock-exam-sections/{section_pk}/edit/',
    })


# ─────────────────────────────────────────────────────────────────────────────
# Mock Exam Attempts (Submissions)
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def mock_exam_attempt_list(request):
    qs = MockExamAttempt.objects.select_related('user', 'exam__level__level_code').order_by('-started_at')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(user__email__icontains=search) | Q(exam__title__icontains=search))
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'custom_admin/mock_exams/attempt_list.html', {
        'attempts': qs[:200], 'search': search, 'status_filter': status_filter,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Mock Exam Purchases
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def mock_exam_purchase_list(request):
    qs = MockExamPurchase.objects.select_related('user', 'package__level').order_by('-purchase_date')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(user__email__icontains=search) | Q(package__name__icontains=search) | Q(transaction_id__icontains=search))
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        qs = qs.filter(payment_status=status_filter)
    return render(request, 'custom_admin/mock_exams/purchase_list.html', {
        'purchases': qs[:200], 'search': search, 'status_filter': status_filter,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def user_list(request):
    qs = User.objects.all().order_by('-created_at')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
    role_filter = request.GET.get('role', '').strip()
    if role_filter:
        qs = qs.filter(role=role_filter)
    return render(request, 'custom_admin/users/list.html', {
        'users': qs[:300], 'search': search, 'role_filter': role_filter,
        'total': User.objects.count(),
        'students': User.objects.filter(role='STUDENT').count(),
        'admins': User.objects.filter(Q(role='ADMIN') | Q(is_superuser=True)).count(),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Enrollments
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def enrollment_list(request):
    qs = Enrollment.objects.select_related('user', 'course', 'level__level_code', 'payment_transaction').order_by('-enrolled_at')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(user__email__icontains=search) | Q(course__name__icontains=search))
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'custom_admin/enrollments/list.html', {
        'enrollments': qs[:300], 'search': search, 'status_filter': status_filter,
        'total': Enrollment.objects.count(),
        'active': Enrollment.objects.filter(status='ACTIVE').count(),
    })


# ─────────────────────────────────────────────────────────────────────────────
# Payments
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def payment_list(request):
    qs = PaymentTransaction.objects.select_related('user', 'course', 'level__level_code').order_by('-created_at')
    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(Q(user__email__icontains=search) | Q(transaction_id__icontains=search) | Q(course__name__icontains=search))
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        qs = qs.filter(status=status_filter)
    return render(request, 'custom_admin/payments/list.html', {
        'payments': qs[:300], 'search': search, 'status_filter': status_filter,
        'total': PaymentTransaction.objects.count(),
        'successful': PaymentTransaction.objects.filter(status='SUCCESS').count(),
    })
