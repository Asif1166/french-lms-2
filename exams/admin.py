from django.contrib import admin
from .models import (
    ExerciseContext, Question, Option, Submission, MockExam, 
    MockExamSection, MockExamQuestion, MockExamAttempt,
    MockExamPackage, PackageFeature, MockExamPurchase, MockExamAccess
)



class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'question_type', 'marks', 'order_index']
    show_change_link = True


class OptionInline(admin.TabularInline):
    model = Option
    extra = 2
    fields = ['text', 'file', 'is_correct', 'order_index', 'match_key']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question_type', 'video', 'level', 'marks', 'order_index', 'is_active']
    list_filter = ['question_type', 'is_active', 'level']
    search_fields = ['text', 'instruction', 'passage']
    ordering = ['video', 'order_index']
    inlines = [OptionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('video', 'level', 'exercise_context', 'question_type', 'text', 'instruction', 'marks', 'order_index', 'is_active')
        }),
        ('Content', {
            'fields': ('passage', 'audio_url', 'image', 'audio_file'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExerciseContext)
class ExerciseContextAdmin(admin.ModelAdmin):
    list_display = ['label', 'video', 'total_points', 'order_index']
    list_filter = ['video']
    search_fields = ['label', 'title', 'context_text']
    ordering = ['video', 'order_index']
    inlines = [QuestionInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('video', 'label', 'order_index', 'total_points')
        }),
        ('Content', {
            'fields': ('title', 'context_text', 'audio_url', 'audio_file')
        }),
    )


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct', 'order_index']
    list_filter = ['is_correct', 'question__question_type']
    search_fields = ['text', 'question__text']
    ordering = ['question', 'order_index']
    fieldsets = (
        ('Basic Information', {
            'fields': ('question', 'text','file', 'is_correct', 'order_index', 'match_key')
        }),
    )

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'score', 'max_score', 'review_status', 'submitted_at']
    list_filter = ['review_status', 'question__question_type', 'submitted_at']
    search_fields = ['user__email', 'question__text', 'answer_text']
    ordering = ['-submitted_at']
    readonly_fields = ['submitted_at', 'updated_at']
    fieldsets = (
        ('Submission Info', {
            'fields': ('user', 'question', 'submitted_at', 'updated_at')
        }),
        ('Answer', {
            'fields': ('answer_text', 'selected_options', 'file_upload')
        }),
        ('Grading', {
            'fields': ('score', 'max_score', 'review_status', 'reviewed_by', 'reviewed_at', 'feedback')
        }),
    )


class MockExamQuestionInline(admin.TabularInline):
    model = MockExamQuestion
    extra = 1
    fields = ['question', 'order_index']


class MockExamSectionInline(admin.TabularInline):
    model = MockExamSection
    extra = 1
    fields = ['title', 'duration_minutes', 'marks', 'order_index']


@admin.register(MockExam)
class MockExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'duration_minutes', 'total_marks', 'is_active', 'created_at']
    list_filter = ['level', 'is_active']
    search_fields = ['title', 'description']
    inlines = [MockExamSectionInline]


@admin.register(MockExamSection)
class MockExamSectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam', 'duration_minutes', 'marks', 'order_index']
    list_filter = ['exam']
    ordering = ['exam', 'order_index']
    inlines = [MockExamQuestionInline]


@admin.register(MockExamQuestion)
class MockExamQuestionAdmin(admin.ModelAdmin):
    list_display = ['section', 'question', 'order_index']
    list_filter = ['section__exam']
    ordering = ['section', 'order_index']


@admin.register(MockExamAttempt)
class MockExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'status', 'total_score', 'started_at', 'submitted_at']
    list_filter = ['status', 'exam__level', 'started_at']
    search_fields = ['user__email', 'exam__title']
    ordering = ['-started_at']
    readonly_fields = ['started_at', 'submitted_at']


@admin.register(PackageFeature)
class PackageFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'created_at']
    search_fields = ['name']


@admin.register(MockExamPackage)
class MockExamPackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'price', 'currency', 'exam_count', 'is_active', 'is_popular', 'display_order']
    list_filter = ['level', 'is_active', 'is_popular']
    search_fields = ['name', 'description']
    ordering = ['display_order', 'level']
    fieldsets = (
        ('Basic Information', {
            'fields': ('level', 'name', 'description', 'display_order')
        }),
        ('Pricing', {
            'fields': ('price', 'currency', 'exam_count')
        }),
        ('Features', {
            'fields': ('features', 'is_active', 'is_popular')
        }),
    )
    filter_horizontal = ['features']


@admin.register(MockExamPurchase)
class MockExamPurchaseAdmin(admin.ModelAdmin):
    list_display = ['user', 'package', 'amount_paid', 'payment_status', 'purchase_date', 'transaction_id']
    list_filter = ['payment_status', 'package__level', 'purchase_date']
    search_fields = ['user__email', 'package__name', 'transaction_id']
    ordering = ['-purchase_date']
    readonly_fields = ['purchase_date']
    actions = ['mark_as_completed', 'grant_exam_access']
    
    fieldsets = (
        ('Purchase Information', {
            'fields': ('user', 'package', 'purchase_date')
        }),
        ('Payment Details', {
            'fields': ('payment_status', 'amount_paid', 'currency', 'transaction_id', 'payment_method')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def mark_as_completed(self, request, queryset):
        for purchase in queryset:
            purchase.payment_status = 'completed'
            purchase.save()
            purchase.grant_access()
        self.message_user(request, f"{queryset.count()} purchases marked as completed and access granted.")
    mark_as_completed.short_description = "Mark selected purchases as completed and grant access"
    
    def grant_exam_access(self, request, queryset):
        for purchase in queryset:
            purchase.grant_access()
        self.message_user(request, f"Access granted for {queryset.count()} purchases.")
    grant_exam_access.short_description = "Grant exam access for selected purchases"


@admin.register(MockExamAccess)
class MockExamAccessAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'granted_via_purchase', 'granted_at', 'is_active']
    list_filter = ['is_active', 'exam__level', 'granted_at']
    search_fields = ['user__email', 'exam__title']
    ordering = ['-granted_at']
    readonly_fields = ['granted_at']


