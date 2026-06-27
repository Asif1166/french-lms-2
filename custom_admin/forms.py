from django import forms
from courses.models import (
    LevelCode, Level, Chapter,
    VideoLesson, LessonResource, WordMeaning, Course,
)
from exams.models import (
    ExerciseContext, Question, Option,
    MockExam, MockExamPackage, PackageFeature, MockExamSection,
)


class LevelCodeForm(forms.ModelForm):
    class Meta:
        model = LevelCode
        fields = ['code', 'name']


class LevelForm(forms.ModelForm):
    class Meta:
        model = Level
        fields = ['level_code', 'title', 'description', 'price',
                  'discounted_price', 'currency', 'order_index', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discounted_price'].required = False





class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['course', 'title', 'description', 'objectives',
                  'grammar_focus', 'vocabulary_list', 'cultural_notes',
                  'exam_relevance', 'order_index', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['grammar_focus', 'vocabulary_list', 'cultural_notes', 'exam_relevance']:
            self.fields[f].required = False


class VideoLessonForm(forms.ModelForm):
    class Meta:
        model = VideoLesson
        fields = ['chapter', 'title', 'description', 'learning_goals',
                  'grammar_explanation', 'vocabulary_explanation', 'example_dialogues',
                  'video_url', 'video_file', 'duration', 'thumbnail',
                  'order_index', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['grammar_explanation', 'vocabulary_explanation',
                  'example_dialogues', 'video_url', 'video_file', 'thumbnail']:
            self.fields[f].required = False


class LessonResourceForm(forms.ModelForm):
    class Meta:
        model = LessonResource
        fields = ['video', 'title', 'file', 'resource_type', 'order_index']


class WordMeaningForm(forms.ModelForm):
    class Meta:
        model = WordMeaning
        fields = ['video', 'word', 'ipa_pronunciation', 'meaning', 'audio_file', 'order_index']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ipa_pronunciation'].required = False
        self.fields['audio_file'].required = False


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'description', 'learning_outcomes', 'level', 'image', 'price',
                  'currency', 'is_full_access', 'duration_months', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level'].required = False
        self.fields['image'].required = False
        self.fields['duration_months'].required = False


class ExerciseContextForm(forms.ModelForm):
    class Meta:
        model = ExerciseContext
        fields = ['video', 'label', 'title', 'context_text', 'total_points',
                  'order_index', 'audio_url', 'audio_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['context_text'].required = False
        self.fields['total_points'].required = False
        self.fields['audio_url'].required = False
        self.fields['audio_file'].required = False


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['video', 'exercise_context', 'question_type', 'text',
                  'instruction', 'marks', 'order_index', 'is_active',
                  'audio_url', 'audio_file', 'passage', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['instruction'].required = False
        self.fields['audio_url'].required = False
        self.fields['audio_file'].required = False
        self.fields['passage'].required = False
        self.fields['image'].required = False
        self.fields['video'].required = False


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['question', 'text', 'file', 'is_correct', 'order_index', 'match_key']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].required = False
        self.fields['match_key'].required = False
        self.fields['text'].required = False


class MockExamForm(forms.ModelForm):
    class Meta:
        model = MockExam
        fields = ['level', 'title', 'description', 'duration_minutes',
                  'total_marks', 'package', 'is_free', 'included_with_enrollment', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['package'].required = False


class MockExamPackageForm(forms.ModelForm):
    class Meta:
        model = MockExamPackage
        fields = ['level', 'name', 'description', 'price', 'currency',
                  'exam_count', 'features', 'is_active', 'is_popular', 'display_order']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['features'].required = False


class PackageFeatureForm(forms.ModelForm):
    class Meta:
        model = PackageFeature
        fields = ['name', 'icon']


class MockExamSectionForm(forms.ModelForm):
    class Meta:
        model = MockExamSection
        fields = ['exam', 'title', 'description', 'duration_minutes', 'marks', 'order_index']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False

