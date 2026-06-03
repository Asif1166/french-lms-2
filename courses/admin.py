from django.contrib import admin
from .models import Level, Category, Chapter, VideoLesson, Course


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'price', 'discounted_price', 'currency', 'order_index', 'is_active', 'created_at']
    list_filter = ['is_active', 'code']
    search_fields = ['code', 'title', 'description']
    ordering = ['order_index', 'code']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order_index']
    ordering = ['order_index']


class VideoLessonInline(admin.TabularInline):
    model = VideoLesson
    extra = 1
    fields = ['title', 'category', 'order_index', 'duration', 'is_active']


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'order_index', 'is_active', 'created_at']
    list_filter = ['level', 'is_active']
    search_fields = ['title', 'description', 'objectives']
    ordering = ['level', 'order_index']
    inlines = [VideoLessonInline]


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'category', 'duration', 'order_index', 'is_active']
    list_filter = ['chapter__level', 'category', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['chapter', 'order_index']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'price', 'currency', 'is_full_access', 'is_active', 'created_at']
    list_filter = ['level', 'is_full_access', 'is_active', 'currency']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
