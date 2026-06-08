from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class LevelCode(models.Model):
    code = models.CharField(max_length=20, unique=True, help_text="e.g. A1, A2, B1, B2")
    name = models.CharField(max_length=100, blank=True, help_text="Optional description/name of the level code")

    class Meta:
        db_table = 'level_codes'
        verbose_name = 'Level Code'
        verbose_name_plural = 'Level Codes'

    def __str__(self):
        return self.code


class Level(models.Model):
    """
    CEFR Levels: A1, A2, B1, B2
    """
    level_code = models.ForeignKey(LevelCode, on_delete=models.PROTECT, null=True, blank=False, related_name='levels')
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='EUR')
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'levels'
        ordering = ['order_index', 'level_code__code']
        verbose_name = 'Level'
        verbose_name_plural = 'Levels'
    
    @property
    def code(self):
        return self.level_code.code if self.level_code else ""

    @code.setter
    def code(self, value):
        if value:
            level_code_obj, _ = LevelCode.objects.get_or_create(code=value)
            self.level_code = level_code_obj
        else:
            self.level_code = None

    def __str__(self):
        return f"{self.code} - {self.title}"


class Category(models.Model):
    """
    Skill Categories: Listening, Reading, Writing, Speaking
    """
    NAME_CHOICES = [
        ('LISTENING', 'Compréhension de l\'oral (Listening)'),
        ('READING', 'Compréhension des écrits (Reading)'),
        ('WRITING', 'Production écrite (Writing)'),
        ('SPEAKING', 'Production orale (Speaking)'),
    ]
    
    name = models.CharField(max_length=50, choices=NAME_CHOICES, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    order_index = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'categories'
        ordering = ['order_index']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.get_name_display()


class Chapter(models.Model):
    """
    Chapters within each Level
    """
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=200)
    description = models.TextField()
    objectives = models.TextField(help_text="Learning objectives for this chapter")
    grammar_focus = models.TextField(blank=True, help_text="Grammar topics covered")
    vocabulary_list = models.TextField(blank=True, help_text="Key vocabulary")
    cultural_notes = models.TextField(blank=True, help_text="Cultural context")
    exam_relevance = models.TextField(blank=True, help_text="How this relates to DELF/DALF")
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chapters'
        ordering = ['level', 'order_index']
        unique_together = ['level', 'order_index']
        verbose_name = 'Chapter'
        verbose_name_plural = 'Chapters'
    
    def __str__(self):
        return f"{self.level.code} - {self.title}"


class VideoLesson(models.Model):
    """
    Video lessons within chapters
    """
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='videos')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField()
    learning_goals = models.TextField(help_text="What students will learn")
    grammar_explanation = models.TextField(blank=True)
    vocabulary_explanation = models.TextField(blank=True)
    example_dialogues = models.TextField(blank=True)
    video_url = models.URLField(help_text="URL to video file (YouTube, Vimeo, or direct link)", blank=True, null=True)
    video_file = models.FileField(upload_to='course_videos/', blank=True, null=True, help_text="Upload video file directly (alternative to Video URL)")
    duration = models.IntegerField(help_text="Duration in seconds", validators=[MinValueValidator(1)])
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'video_lessons'
        ordering = ['chapter', 'order_index']
        verbose_name = 'Video Lesson'
        verbose_name_plural = 'Video Lessons'
    
    def __str__(self):
        return f"{self.chapter.level.code} - {self.title}"
    
    def get_duration_display(self):
        """Convert seconds to MM:SS format"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_embed_url(self):
        """Convert YouTube URL to embed format"""
        if 'youtube.com/watch?v=' in self.video_url:
            video_id = self.video_url.split('watch?v=')[1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        elif 'youtu.be/' in self.video_url:
            video_id = self.video_url.split('youtu.be/')[1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.video_url


class Course(models.Model):
    """
    Course/Package for payment and enrollment
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='EUR')
    is_full_access = models.BooleanField(default=False, help_text="If True, provides access to all levels")
    duration_months = models.IntegerField(null=True, blank=True, help_text="Access duration in months (null = lifetime)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
    
    def __str__(self):
        return self.name


class LessonResource(models.Model):
    """
    Additional resources for a video lesson (PDF, Images, etc.)
    """
    RESOURCE_TYPE_CHOICES = [
        ('PDF', 'PDF Document'),
        ('IMAGE', 'Image'),
        ('DOC', 'Document'),
        ('OTHER', 'Other'),
    ]
    
    video = models.ForeignKey(VideoLesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='lesson_resources/')
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPE_CHOICES, default='PDF')
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lesson_resources'
        ordering = ['order_index']
        verbose_name = 'Lesson Resource'
        verbose_name_plural = 'Lesson Resources'

    def __str__(self):
        return f"{self.video.title} - {self.title}"


class WordMeaning(models.Model):
    """
    Vocabulary/Word Meanings for a video lesson.
    """
    video = models.ForeignKey(VideoLesson, on_delete=models.CASCADE, related_name='word_meanings')
    word = models.CharField(max_length=200, help_text="Word or phrase in French")
    ipa_pronunciation = models.CharField(max_length=200, blank=True, help_text="IPA phonetic transcription (optional)")
    meaning = models.TextField(help_text="Meaning of the word in text (e.g. English or Bengali)")
    audio_file = models.FileField(upload_to='word_pronunciations/', blank=True, null=True, help_text="Audio file for pronunciation")
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'word_meanings'
        ordering = ['order_index', 'word']
        verbose_name = 'Word Meaning'
        verbose_name_plural = 'Word Meanings'

    def __str__(self):
        return f"{self.word} - {self.meaning}"

