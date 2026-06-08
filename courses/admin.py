from django.contrib import admin
from .models import Level, LevelCode, Category, Chapter, VideoLesson, Course, WordMeaning



@admin.register(LevelCode)
class LevelCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'price', 'discounted_price', 'currency', 'order_index', 'is_active', 'created_at']
    list_filter = ['is_active', 'level_code']
    search_fields = ['level_code__code', 'title', 'description']
    ordering = ['order_index', 'level_code__code']


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


class WordMeaningInline(admin.TabularInline):
    model = WordMeaning
    extra = 1
    fields = ['word', 'ipa_pronunciation', 'meaning', 'audio_file', 'order_index']


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'category', 'duration', 'order_index', 'is_active']
    list_filter = ['chapter__level', 'category', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['chapter', 'order_index']
    inlines = [WordMeaningInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'price', 'currency', 'is_full_access', 'is_active', 'created_at']
    list_filter = ['level', 'is_full_access', 'is_active', 'currency']
    search_fields = ['name', 'description']
    ordering = ['-created_at']


@admin.register(WordMeaning)
class WordMeaningAdmin(admin.ModelAdmin):
    list_display = ['word', 'video', 'ipa_pronunciation', 'meaning', 'order_index']
    list_filter = ['video__chapter__level', 'video']
    search_fields = ['word', 'meaning']
    ordering = ['video', 'order_index', 'word']

