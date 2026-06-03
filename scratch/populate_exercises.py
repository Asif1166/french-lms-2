import os
import django
import sys

# Set up Django environment
sys.path.append('/home/asif/DEV/french_lms')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'french_lms.settings')
django.setup()

from courses.models import VideoLesson, Level
from exams.models import Question, Option, ExerciseContext

def populate_exercises():
    print("Populating Practice Exercises...")

    # A1 Exercises
    a1_lessons = VideoLesson.objects.filter(chapter__level__code='A1')
    for lesson in a1_lessons:
        if 'Salutations' in lesson.title:
            ctx = ExerciseContext.objects.create(
                video=lesson,
                label='EXERCICE 1',
                title='Les salutations de base',
                context_text='Choisissez la bonne réponse pour chaque situation.',
                order_index=1
            )
            
            q1 = Question.objects.create(
                video=lesson,
                exercise_context=ctx,
                question_type='MCQ_SINGLE',
                text='Comment dit-on "Good morning" en français?',
                instruction='Choisissez une seule réponse.',
                marks=1,
                order_index=1
            )
            Option.objects.create(question=q1, text='Bonsoir', is_correct=False, order_index=1)
            Option.objects.create(question=q1, text='Bonjour', is_correct=True, order_index=2)
            Option.objects.create(question=q1, text='Bonne nuit', is_correct=False, order_index=3)

            q2 = Question.objects.create(
                video=lesson,
                exercise_context=ctx,
                question_type='FILL_BLANK',
                text='Enchanté, je m\'appelle Marie. Et ____ ? (You - formal)',
                instruction='Écrivez le mot manquant.',
                marks=1,
                order_index=2
            )
            # For FILL_BLANK, we might store the answer in a specific way or just leave it for manual review
            # Assuming auto-grading logic might check Option for FILL_BLANK too
            Option.objects.create(question=q2, text='vous', is_correct=True, order_index=1)

        elif 'Compter' in lesson.title:
            ctx = ExerciseContext.objects.create(
                video=lesson,
                label='EXERCICE 1',
                title='Les nombres de 1 à 20',
                context_text='Écoutez et écrivez les nombres en lettres.',
                order_index=1
            )
            q1 = Question.objects.create(
                video=lesson,
                exercise_context=ctx,
                question_type='MCQ_SINGLE',
                text='Quel est le nombre "Quinze"?',
                marks=1,
                order_index=1
            )
            Option.objects.create(question=q1, text='5', is_correct=False, order_index=1)
            Option.objects.create(question=q1, text='15', is_correct=True, order_index=2)
            Option.objects.create(question=q1, text='50', is_correct=False, order_index=3)

    # A2 Exercises
    a2_lessons = VideoLesson.objects.filter(chapter__level__code='A2')
    for lesson in a2_lessons:
        if 'Ma Routine' in lesson.title:
            ctx = ExerciseContext.objects.create(
                video=lesson,
                label='EXERCICE 1',
                title='La vie quotidienne',
                context_text='Vrai ou Faux? Lisez les phrases sur la routine de Marc.',
                order_index=1
            )
            q1 = Question.objects.create(
                video=lesson,
                exercise_context=ctx,
                question_type='TRUE_FALSE',
                text='Marc se réveille à 7 heures du matin.',
                marks=1,
                order_index=1
            )
            Option.objects.create(question=q1, text='Vrai', is_correct=True, order_index=1)
            Option.objects.create(question=q1, text='Faux', is_correct=False, order_index=2)

    # B1 Exercises
    b1_lessons = VideoLesson.objects.filter(chapter__level__code='B1')
    for lesson in b1_lessons:
        if 'Donner son opinion' in lesson.title:
            ctx = ExerciseContext.objects.create(
                video=lesson,
                label='EXERCICE 1',
                title='Exprimer un point de vue',
                context_text='Complétez avec l\'expression appropriée.',
                order_index=1
            )
            q1 = Question.objects.create(
                video=lesson,
                exercise_context=ctx,
                question_type='MCQ_SINGLE',
                text='À mon ____, le télétravail est une bonne idée.',
                marks=1,
                order_index=1
            )
            Option.objects.create(question=q1, text='avis', is_correct=True, order_index=1)
            Option.objects.create(question=q1, text='vue', is_correct=False, order_index=2)
            Option.objects.create(question=q1, text='penser', is_correct=False, order_index=3)

    # B2 Exercises
    b2_lessons = VideoLesson.objects.filter(chapter__level__code='B2')
    for lesson in b2_lessons:
        if 'Débats de Société' in lesson.title:
            ctx = ExerciseContext.objects.create(
                video=lesson,
                label='EXERCICE 1',
                title='Compréhension orale',
                context_text='Analysez l\'argumentaire de l\'intervenant.',
                order_index=1
            )
            q1 = Question.objects.create(
                video=lesson,
                exercise_context=ctx,
                question_type='MCQ_SINGLE',
                text='Quel est le principal argument en faveur de la réforme?',
                marks=2,
                order_index=1
            )
            Option.objects.create(question=q1, text='L\'économie nationale', is_correct=True, order_index=1)
            Option.objects.create(question=q1, text='Le bien-être social', is_correct=False, order_index=2)
            Option.objects.create(question=q1, text='La pression internationale', is_correct=False, order_index=3)

    print("Practice Exercises population complete!")

if __name__ == "__main__":
    populate_exercises()
