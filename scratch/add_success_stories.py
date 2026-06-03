import os
import django
import sys

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'french_lms.settings')
django.setup()

from dashboard.models import SuccessStory

stories = [
    {
        "student_name": "Rahat Ahmed",
        "student_image": None,
        "story_text": "Starting from zero, I never thought I could speak French so fluently. The structured modules and mock exams made the difference. Highly recommended for DELF preparation!",
        "level_achieved": "B2",
        "rating": 5,
        "is_active": True
    },
    {
        "student_name": "Sultana Razia",
        "student_image": None,
        "story_text": "The interactive 3D materials are a game changer. I cleared my A2 exam with 90+ marks thanks to the amazing instructors and clear explanations.",
        "level_achieved": "A2",
        "rating": 5,
        "is_active": True
    }
]

for story in stories:
    SuccessStory.objects.create(**story)
    print(f"Created success story for {story['student_name']}")
