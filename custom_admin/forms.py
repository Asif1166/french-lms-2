from django import forms
from courses.models import (
    LevelCode, Level, Category, Chapter,
    VideoLesson, LessonResource, WordMeaning, Course,
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


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'order_index']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['icon'].required = False


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ['level', 'title', 'description', 'objectives',
                  'grammar_focus', 'vocabulary_list', 'cultural_notes',
                  'exam_relevance', 'order_index', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['grammar_focus', 'vocabulary_list', 'cultural_notes', 'exam_relevance']:
            self.fields[f].required = False


class VideoLessonForm(forms.ModelForm):
    class Meta:
        model = VideoLesson
        fields = ['chapter', 'category', 'title', 'description', 'learning_goals',
                  'grammar_explanation', 'vocabulary_explanation', 'example_dialogues',
                  'video_url', 'video_file', 'duration', 'thumbnail',
                  'order_index', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['category', 'grammar_explanation', 'vocabulary_explanation',
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
        fields = ['name', 'description', 'learning_outcomes', 'level', 'chapters', 'image', 'price',
                  'currency', 'is_full_access', 'duration_months', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['level'].required = False
        self.fields['image'].required = False
        self.fields['duration_months'].required = False
        self.fields['chapters'].required = False
        self.fields['chapters'].queryset = Chapter.objects.select_related(
            'level__level_code'
        ).order_by('level__level_code__code', 'order_index')
