from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Level, Chapter, VideoLesson, WordMeaning, Course
from enrollments.models import Enrollment

User = get_user_model()

class WordMeaningTestCase(TestCase):
    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            email='teststudent@gmail.com',
            username='teststudent',
            password='testpassword',
            role='STUDENT'
        )
        
        # Create courses setup
        self.level = Level.objects.create(
            code='A1',
            title='A1 Beginner',
            description='Beginner level',
            price=10.00,
            order_index=1,
            is_active=True
        )

        self.course = Course.objects.create(
            name='French A1',
            description='A1 Beginner Course',
            level=self.level,
            price=10.00,
            is_active=True
        )

        
        self.chapter = Chapter.objects.create(
            level=self.level,
            title='Chapter 1',
            description='Intro to French',
            objectives='Learn greetings',
            order_index=1,
            is_active=True
        )
        
        self.video = VideoLesson.objects.create(
            chapter=self.chapter,
            title='Lesson 1: Greetings',
            description='Greetings lesson',
            learning_goals='Say Bonjour',
            duration=300,
            order_index=1,
            is_active=True
        )
        
        # Create active enrollment
        self.enrollment = Enrollment.objects.create(
            user=self.user,
            level=self.level,
            status='ACTIVE'
        )
        
        # Create Word meanings
        self.word1 = WordMeaning.objects.create(
            video=self.video,
            word='Bonjour',
            ipa_pronunciation='/bɔ̃.ʒuʁ/',
            meaning='Hello / Good morning',
            order_index=1
        )
        self.word2 = WordMeaning.objects.create(
            video=self.video,
            word='Au revoir',
            ipa_pronunciation='/o ʁə.vwaʁ/',
            meaning='Goodbye',
            order_index=2
        )

    def test_word_meaning_creation(self):
        self.assertEqual(str(self.word1), "Bonjour - Hello / Good morning")
        self.assertEqual(self.word1.video, self.video)
        self.assertEqual(self.word1.ipa_pronunciation, "/bɔ̃.ʒuʁ/")

    def test_video_detail_view_context_and_template(self):
        self.client.login(email='teststudent@gmail.com', password='testpassword')
        
        url = reverse('courses:video_detail', kwargs={'video_id': self.video.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Check that word meanings are in the context
        self.assertIn('word_meanings', response.context)
        word_meanings = list(response.context['word_meanings'])
        self.assertEqual(len(word_meanings), 2)
        self.assertEqual(word_meanings[0].word, "Bonjour")
        self.assertEqual(word_meanings[1].word, "Au revoir")
        
        # Check template content presence (the new tab and the cards)
        self.assertContains(response, 'data-tab="wordmeanings"')
        self.assertContains(response, 'id="wordmeanings-pane"')
        self.assertContains(response, 'Bonjour')
        self.assertContains(response, '/bɔ̃.ʒuʁ/')
        self.assertContains(response, 'Hello / Good morning')

