import os
import django
import sys

# Set up Django environment
sys.path.append('/home/asif/DEV/french_lms')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'french_lms.settings')
django.setup()

from courses.models import Level, Category
from exams.models import MockExam, MockExamSection, MockExamQuestion, Question, Option, ExerciseContext

def populate_mock_questions():
    print("Populating Mock Exam Questions...")

    exams = MockExam.objects.all()
    
    for exam in exams:
        level = exam.level
        sections = exam.sections.all()
        
        for section in sections:
            cat_name = section.category.name
            
            if cat_name == 'LISTENING':
                # Create an exercise context for listening
                ctx = ExerciseContext.objects.create(
                    label='EXERCICE 1',
                    title='Compréhension de l\'oral',
                    context_text='Écoutez le document sonore et répondez aux questions.',
                    order_index=1
                )
                
                # Question 1
                q1 = Question.objects.create(
                    level=level,
                    exercise_context=ctx,
                    question_type='MCQ_SINGLE',
                    text='Quel est le sujet principal de la conversation?',
                    instruction='Choisissez la bonne réponse.',
                    marks=5,
                    order_index=1
                )
                Option.objects.create(question=q1, text='Une fête d\'anniversaire', is_correct=True, order_index=1)
                Option.objects.create(question=q1, text='Un voyage d\'affaires', is_correct=False, order_index=2)
                Option.objects.create(question=q1, text='Un cours de français', is_correct=False, order_index=3)
                
                MockExamQuestion.objects.create(section=section, question=q1, order_index=1)

                # Question 2
                q2 = Question.objects.create(
                    level=level,
                    exercise_context=ctx,
                    question_type='TRUE_FALSE',
                    text='L\'homme est d\'accord avec la proposition de la femme.',
                    marks=5,
                    order_index=2
                )
                Option.objects.create(question=q2, text='Vrai', is_correct=False, order_index=1)
                Option.objects.create(question=q2, text='Faux', is_correct=True, order_index=2)
                
                MockExamQuestion.objects.create(section=section, question=q2, order_index=2)

            elif cat_name == 'READING':
                ctx = ExerciseContext.objects.create(
                    label='EXERCICE 2',
                    title='Compréhension des écrits',
                    context_text='Lisez ce courriel et répondez aux questions.',
                    order_index=1
                )
                
                q1 = Question.objects.create(
                    level=level,
                    exercise_context=ctx,
                    question_type='MCQ_SINGLE',
                    text='Qui a envoyé ce message?',
                    marks=5,
                    order_index=1
                )
                Option.objects.create(question=q1, text='Le directeur de l\'école', is_correct=True, order_index=1)
                Option.objects.create(question=q1, text='Un étudiant', is_correct=False, order_index=2)
                
                MockExamQuestion.objects.create(section=section, question=q1, order_index=1)

            elif cat_name == 'WRITING':
                q1 = Question.objects.create(
                    level=level,
                    question_type='EMAIL_WRITING',
                    text='Vous écrivez un courriel à un ami pour l\'inviter à votre fête.',
                    instruction='Écrivez au moins 60 mots.',
                    marks=25,
                    order_index=1
                )
                MockExamQuestion.objects.create(section=section, question=q1, order_index=1)

            elif cat_name == 'SPEAKING':
                q1 = Question.objects.create(
                    level=level,
                    question_type='ROLE_PLAY',
                    text='Sujet: Faire des courses au marché.',
                    instruction='Préparez un dialogue de 2-3 minutes.',
                    marks=25,
                    order_index=1
                )
                MockExamQuestion.objects.create(section=section, question=q1, order_index=1)

    print("Mock Questions population complete!")

if __name__ == "__main__":
    populate_mock_questions()
