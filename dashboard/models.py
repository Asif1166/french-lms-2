from django.db import models
from django.utils.text import slugify
from django.conf import settings

class FAQCategory(models.Model):
    name = models.CharField(max_length=200, verbose_name="ক্যাটাগরি নাম")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="স্লাগ")
    order = models.PositiveIntegerField(default=0, verbose_name="ক্রম")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class FAQ(models.Model):
    category = models.ForeignKey(FAQCategory, on_delete=models.CASCADE, related_name='faqs', null=True, blank=True, verbose_name="ক্যাটাগরি")
    question = models.CharField(max_length=500, verbose_name="প্রশ্ন")
    answer = models.TextField(verbose_name="উত্তর")
    order = models.PositiveIntegerField(default=0, verbose_name="ক্রম")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['order', 'created_at']

    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.name}: {self.subject}"


class SuccessStory(models.Model):
    student_name = models.CharField(max_length=100)
    level = models.CharField(max_length=50, blank=True)
    testimony = models.TextField()
    photo = models.ImageField(upload_to='success_stories/')
    order_index = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Success Stories"
        ordering = ['order_index', '-created_at']

    def __str__(self):
        return self.student_name


class InstructorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='instructor_profile')
    designation = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Senior French Instructor")
    bio = models.TextField()
    expertise = models.CharField(max_length=200, help_text="e.g. DELF A1/A2, Business French")
    photo = models.ImageField(upload_to='instructors/', blank=True, null=True)
    experience_years = models.PositiveIntegerField(default=0)
    total_students = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    facebook_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    order_index = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order_index', 'user__first_name']

    def __str__(self):
        return f"Instructor: {self.user.get_full_name() or self.user.username}"


class CommunityStory(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, help_text="e.g. Frontend Developer")
    location = models.CharField(max_length=100, help_text="e.g. Norway")
    photo = models.ImageField(upload_to='community_stories/')
    bio = models.TextField(blank=True, null=True, help_text="Short biography")
    full_story = models.TextField(blank=True, null=True, help_text="Detailed story content")
    quote = models.TextField(blank=True, null=True, help_text="Featured quote")
    story_url = models.URLField(blank=True, null=True, help_text="Optional external link")
    order_index = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Community Stories"
        ordering = ['order_index', '-created_at']

    def __str__(self):
        return self.name
