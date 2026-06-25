from django.contrib import admin
from .models import Enrollment, VideoProgress, ChapterProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'level', 'status', 'enrolled_at', 'expires_at']
    list_filter = ['status', 'course__level', 'level', 'enrolled_at']
    search_fields = ['user__email', 'course__name', 'level__title']
    ordering = ['-enrolled_at']
    readonly_fields = ['enrolled_at', 'created_at', 'updated_at']
    fieldsets = (
        ('Enrollment Info', {
            'fields': ('user', 'course', 'level', 'payment_transaction', 'status')
        }),
        ('Dates', {
            'fields': ('enrolled_at', 'expires_at', 'cancelled_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'is_completed', 'watched_duration', 'last_watched_at']
    list_filter = ['is_completed', 'video__chapter__course']
    search_fields = ['user__email', 'video__title']
    ordering = ['-last_watched_at']


@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'chapter', 'completion_percentage', 'is_completed', 'updated_at']
    list_filter = ['is_completed', 'chapter__course']
    search_fields = ['user__email', 'chapter__title']
    ordering = ['-updated_at']
