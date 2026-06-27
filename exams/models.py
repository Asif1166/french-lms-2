from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from courses.models import VideoLesson, Level
from accounts.models import User


class ExerciseContext(models.Model):
    """
    Shared context/passage for a group of questions
    Example: "EXERCICE 3" with instructions and scenario text
    """
    video = models.ForeignKey(VideoLesson, on_delete=models.CASCADE, related_name='exercise_contexts', null=True, blank=True)
    label = models.CharField(max_length=100, help_text="Exercise label (e.g., 'EXERCICE 3')")
    title = models.TextField(blank=True, help_text="Exercise instructions (e.g., 'Lisez les questions. Écoutez le document puis répondez.')")
    context_text = models.TextField(blank=True, help_text="Scenario or context text (e.g., 'Vous travaillez en France...')")
    total_points = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Total points for this exercise")
    order_index = models.IntegerField(default=0, help_text="Order of this exercise in the video")
    audio_url = models.URLField(blank=True, null=True, help_text="Audio file URL for listening context")
    audio_file = models.FileField(upload_to='exercise_audio/', blank=True, null=True, help_text="Audio file for listening context")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'exercise_contexts'
        ordering = ['video', 'order_index']
        verbose_name = 'Exercise Context'
        verbose_name_plural = 'Exercise Contexts'
    
    def __str__(self):
        return f"{self.label} - {self.video.title if self.video else 'No Video'}"


class Question(models.Model):
    """
    Questions associated with video lessons
    Supports multiple question types inspired by DELF/DALF patterns
    """
    QUESTION_TYPE_CHOICES = [
        # Listening Questions
        ('MCQ_SINGLE', 'Multiple Choice (Single Answer)'),
        ('MCQ_MULTIPLE', 'Multiple Choice (Multiple Answers)'),
        ('TRUE_FALSE', 'True / False'),
        ('FILL_BLANK', 'Fill in the Blank'),
        ('MATCHING', 'Matching'),
        # Reading Questions
        ('YES_NO_NOT_MENTIONED', 'Yes / No / Not Mentioned'),
        ('INFORMATION_EXTRACTION', 'Information Extraction'),
        # Writing Questions
        ('EMAIL_WRITING', 'Email Writing'),
        ('SHORT_PARAGRAPH', 'Short Paragraph'),
        ('OPINION_TEXT', 'Opinion-based Text'),
        # Speaking Questions
        ('ROLE_PLAY', 'Role-play Simulation'),
        ('IMAGE_DESCRIPTION', 'Image-based Description'),
        ('TOPIC_MONOLOGUE', 'Topic Monologue'),
    ]
    
    video = models.ForeignKey(VideoLesson, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    exercise_context = models.ForeignKey(ExerciseContext, on_delete=models.SET_NULL, related_name='questions', null=True, blank=True, help_text="Shared context for this question")
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPE_CHOICES)
    text = models.TextField(help_text="Question text or prompt")
    instruction = models.TextField(blank=True, help_text="Instructions for answering (e.g., 'Choose the best answer', 'Fill in the blanks')")
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, validators=[MinValueValidator(0)])
    order_index = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For listening questions - audio file
    audio_url = models.URLField(blank=True, null=True, help_text="Audio file URL for listening questions")
    
    audio_file = models.FileField(upload_to='question_audio/', blank=True, null=True, help_text="Audio file for listening questions")

    # For reading questions - passage
    passage = models.TextField(blank=True, help_text="Reading passage or text")
    
    # For image-based questions
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['video', 'order_index']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
    
    def __str__(self):
        return f"{self.get_question_type_display()} - {self.text[:50]}..."


class Option(models.Model):
    """
    Options for MCQ, True/False, Matching questions
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='option_file/', blank=True, null=True, help_text="File for option")
    is_correct = models.BooleanField(default=False)
    order_index = models.IntegerField(default=0)
    
    # For matching questions
    match_key = models.CharField(max_length=100, blank=True, help_text="Key for matching pairs")
    
    class Meta:
        db_table = 'options'
        ordering = ['question', 'order_index']
        verbose_name = 'Option'
        verbose_name_plural = 'Options'
    
    def __str__(self):
        return f"{self.question.text[:30]}... - {self.text[:30]}..."


class Submission(models.Model):
    """
    Student submissions for questions
    """
    REVIEW_STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('REVIEWED', 'Reviewed'),
        ('AUTO_GRADED', 'Auto Graded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='submissions')
    answer_text = models.TextField(blank=True, help_text="Text answer for writing/speaking questions")
    selected_options = models.ManyToManyField(Option, blank=True, help_text="Selected options for MCQ questions")
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)])
    max_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    review_status = models.CharField(max_length=20, choices=REVIEW_STATUS_CHOICES, default='PENDING')
    feedback = models.TextField(blank=True, help_text="Instructor feedback")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_submissions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # For file uploads (speaking/writing)
    file_upload = models.FileField(upload_to='submissions/', blank=True, null=True)
    
    class Meta:
        db_table = 'submissions'
        ordering = ['-submitted_at']
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
    
    def __str__(self):
        return f"{self.user.email} - {self.question.text[:30]}..."


class MockExam(models.Model):
    """
    Mock exam for a specific level
    """
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='mock_exams')
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.IntegerField(help_text="Total exam duration in minutes")
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    is_active = models.BooleanField(default=True)
    package = models.ForeignKey('MockExamPackage', on_delete=models.SET_NULL, null=True, blank=True, related_name='exams', help_text="Package this exam belongs to")
    is_free = models.BooleanField(default=False, help_text="If true, exam is accessible without purchase")
    included_with_enrollment = models.BooleanField(default=False, help_text="If true, course-enrolled students get free access")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mock_exams'
        verbose_name = 'Mock Exam'
        verbose_name_plural = 'Mock Exams'
    
    def __str__(self):
        return f"{self.level.code} - {self.title}"


class PackageFeature(models.Model):
    """
    Features included in an exam package
    """
    name = models.CharField(max_length=200, help_text="Feature name (e.g., 'PDF Explanations')")
    icon = models.CharField(max_length=50, default='fas fa-check-circle', help_text="FontAwesome icon class")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'package_features'
        verbose_name = 'Package Feature'
        verbose_name_plural = 'Package Features'

    def __str__(self):
        return self.name


class MockExamPackage(models.Model):
    """
    Represents a purchasable package of mock exams for a specific level
    """
    level = models.ForeignKey('courses.LevelCode', on_delete=models.CASCADE, related_name='mock_exam_packages', db_index=True)
    name = models.CharField(max_length=200, help_text="Package name (e.g., 'A1 Complete Mock Exam Package')")
    description = models.TextField(help_text="Detailed description of what's included")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Package price")
    currency = models.CharField(max_length=3, default='EUR')
    exam_count = models.IntegerField(help_text="Number of exams in this package")
    features = models.ManyToManyField(PackageFeature, blank=True, related_name='packages', help_text="List of features")
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, help_text="Mark as popular/recommended")
    display_order = models.IntegerField(default=0, help_text="Order to display on pricing page")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mock_exam_packages'
        ordering = ['display_order', 'level']
        verbose_name = 'Mock Exam Package'
        verbose_name_plural = 'Mock Exam Packages'
    
    def __str__(self):
        return f"{self.level.code} - {self.name}"

    def get_exam_count(self):
        """Get actual count of exams in this package"""
        return self.exams.filter(is_active=True).count()


class MockExamPurchase(models.Model):
    """
    Tracks user purchases of exam packages
    """
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mock_exam_purchases')
    package = models.ForeignKey(MockExamPackage, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending', db_index=True)
    transaction_id = models.CharField(max_length=200, blank=True, null=True, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    payment_method = models.CharField(max_length=50, blank=True, help_text="Payment method used")
    notes = models.TextField(blank=True, help_text="Additional notes about the purchase")
    
    class Meta:
        db_table = 'mock_exam_purchases'
        ordering = ['-purchase_date']
        verbose_name = 'Mock Exam Purchase'
        verbose_name_plural = 'Mock Exam Purchases'
    
    def __str__(self):
        return f"{self.user.email} - {self.package.name} - {self.payment_status}"
    
    def grant_access(self):
        """Grant user access to all exams in the purchased package"""
        if self.payment_status == 'completed':
            for exam in self.package.exams.filter(is_active=True):
                MockExamAccess.objects.get_or_create(
                    user=self.user,
                    exam=exam,
                    defaults={'granted_via_purchase': self}
                )


class MockExamAccess(models.Model):
    """
    Tracks which users have access to which mock exams
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mock_exam_access')
    exam = models.ForeignKey(MockExam, on_delete=models.CASCADE, related_name='user_access')
    granted_via_purchase = models.ForeignKey(MockExamPurchase, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_access')
    granted_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'mock_exam_access'
        unique_together = ['user', 'exam']
        ordering = ['-granted_at']
        verbose_name = 'Mock Exam Access'
        verbose_name_plural = 'Mock Exam Access'
    
    def __str__(self):
        return f"{self.user.email} - {self.exam.title}"


class MockExamSection(models.Model):
    """
    Sections within a mock exam (Listening, Reading, Writing, Speaking)
    """
    exam = models.ForeignKey(MockExam, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(help_text="Section duration in minutes")
    marks = models.DecimalField(max_digits=5, decimal_places=2, default=25.0)
    order_index = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'mock_exam_sections'
        ordering = ['exam', 'order_index']
        verbose_name = 'Mock Exam Section'
        verbose_name_plural = 'Mock Exam Sections'
    
    def __str__(self):
        return f"{self.exam.title} - {self.title}"


class MockExamQuestion(models.Model):
    """
    Questions in mock exam sections
    """
    section = models.ForeignKey(MockExamSection, on_delete=models.CASCADE, related_name='questions')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='mock_exam_questions')
    order_index = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'mock_exam_questions'
        ordering = ['section', 'order_index']
        unique_together = ['section', 'question']
        verbose_name = 'Mock Exam Question'
        verbose_name_plural = 'Mock Exam Questions'
    
    def __str__(self):
        return f"{self.section.exam.title} - Q{self.order_index}"


class MockExamAttempt(models.Model):
    """
    Student attempt for a mock exam
    """
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('SUBMITTED', 'Submitted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mock_exam_attempts')
    exam = models.ForeignKey(MockExam, on_delete=models.CASCADE, related_name='attempts')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    listening_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    reading_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    writing_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    speaking_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0)
    
    class Meta:
        db_table = 'mock_exam_attempts'
        ordering = ['-started_at']
        verbose_name = 'Mock Exam Attempt'
        verbose_name_plural = 'Mock Exam Attempts'
    
    def __str__(self):
        return f"{self.user.email} - {self.exam.title} - {self.status}"
