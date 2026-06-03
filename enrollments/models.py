from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import User
from courses.models import Course
from payments.models import PaymentTransaction


class Enrollment(models.Model):
    """
    Course enrollments - created after successful payment
    """
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    level = models.ForeignKey('courses.Level', on_delete=models.CASCADE, related_name='enrollments', null=True, blank=True)
    payment_transaction = models.OneToOneField(
        PaymentTransaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='enrollment'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Access expiration date (null = lifetime)")
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'enrollments'
        ordering = ['-enrolled_at']
        unique_together = ['user', 'course']
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'
    
    def __str__(self):
        item_name = self.course.name if self.course else (self.level.title if self.level else "Unknown")
        return f"{self.user.email} - {item_name} - {self.status}"
    
    def is_active(self):
        """Check if enrollment is currently active"""
        if self.status != 'ACTIVE':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
    
    def has_access_to_level(self, level):
        """Check if user has access to a specific level"""
        if not self.is_active():
            return False
        # Full platform access
        if self.course and self.course.is_full_access:
            return True
        # Specific level access via Level enrollment
        if self.level and self.level == level:
            return True
        # Specific level access via Course enrollment
        if self.course and self.course.level and self.course.level == level:
            return True
        return False


class VideoProgress(models.Model):
    """
    Track video watching progress for enrolled users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_progress')
    video = models.ForeignKey('courses.VideoLesson', on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    watched_duration = models.IntegerField(default=0, help_text="Seconds watched")
    last_watched_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'video_progress'
        unique_together = ['user', 'video']
        verbose_name = 'Video Progress'
        verbose_name_plural = 'Video Progress'
    
    def __str__(self):
        return f"{self.user.email} - {self.video.title} - {self.is_completed}"


class ChapterProgress(models.Model):
    """
    Track chapter completion for enrolled users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chapter_progress')
    chapter = models.ForeignKey('courses.Chapter', on_delete=models.CASCADE, related_name='progress')
    completion_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chapter_progress'
        unique_together = ['user', 'chapter']
        verbose_name = 'Chapter Progress'
        verbose_name_plural = 'Chapter Progress'
    
    def __str__(self):
        return f"{self.user.email} - {self.chapter.title} - {self.completion_percentage}%"
