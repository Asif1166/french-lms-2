from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import VideoProgress, ChapterProgress
from courses.models import VideoLesson


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def mark_video_complete_view(request, video_id):
    """Mark video as completed"""
    video = get_object_or_404(VideoLesson, id=video_id)
    
    progress, created = VideoProgress.objects.get_or_create(
        user=request.user,
        video=video
    )
    
    progress.is_completed = True
    progress.watched_duration = video.duration
    progress.save()
    
    # Update chapter progress
    chapter = video.chapter
    total_videos = chapter.videos.filter(is_active=True).count()
    completed_videos = VideoProgress.objects.filter(
        user=request.user,
        video__chapter=chapter,
        is_completed=True
    ).count()
    
    completion_percentage = (completed_videos / total_videos * 100) if total_videos > 0 else 0
    
    chapter_progress, _ = ChapterProgress.objects.get_or_create(
        user=request.user,
        chapter=chapter
    )
    chapter_progress.completion_percentage = completion_percentage
    chapter_progress.is_completed = completion_percentage == 100
    chapter_progress.save()
    
    return JsonResponse({'success': True, 'completion_percentage': completion_percentage})
