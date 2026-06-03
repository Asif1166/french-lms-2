import os
import django
import sys

# Set up Django environment
sys.path.append('/home/asif/DEV/french_lms')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'french_lms.settings')
django.setup()

from courses.models import Level, Category
from exams.models import MockExam, MockExamSection

def populate_mock_exams():
    print("Populating Mock Exams...")

    levels = Level.objects.all()
    categories = Category.objects.all()

    for level in levels:
        # Create a Full Mock Exam for each level
        exam = MockExam.objects.create(
            level=level,
            title=f'Official {level.code} Practice Exam - Version A',
            description=f'This is a complete simulation of the {level.code} DELF exam. It includes all four sections and is timed for realistic practice.',
            duration_minutes=100 if level.code in ['B1', 'B2'] else 60,
            total_marks=100,
            is_active=True
        )

        # Create Sections
        order = 1
        for cat in categories:
            MockExamSection.objects.create(
                exam=exam,
                category=cat,
                title=f'{cat.get_name_display()} Section',
                description=f'Complete the {cat.get_name_display().lower()} tasks.',
                duration_minutes=exam.duration_minutes // 4,
                marks=25,
                order_index=order
            )
            order += 1

    print("Mock Exams population complete!")

if __name__ == "__main__":
    populate_mock_exams()
