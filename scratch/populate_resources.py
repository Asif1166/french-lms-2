import os
import django
import sys
from django.core.files.base import ContentFile

# Set up Django environment
sys.path.append('/home/asif/DEV/french_lms')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'french_lms.settings')
django.setup()

from courses.models import VideoLesson, LessonResource

def populate_resources():
    print("Populating Lesson Resources...")

    # A1 Lesson Resources
    a1_salutations = VideoLesson.objects.filter(title__icontains='Salutations').first()
    if a1_salutations:
        # Create a dummy PDF
        pdf_content = b"%PDF-1.4\n%..."
        r1 = LessonResource(
            video=a1_salutations,
            title='Glossary of Greetings',
            resource_type='PDF',
            order_index=1
        )
        r1.file.save('greetings_glossary.pdf', ContentFile(pdf_content))
        
        # Create a dummy image info
        img_content = b"fake image data"
        r2 = LessonResource(
            video=a1_salutations,
            title='Greeting Infographic',
            resource_type='IMAGE',
            order_index=2
        )
        r2.file.save('greetings_infographic.jpg', ContentFile(img_content))

    # B2 Lesson Resources
    b2_debats = VideoLesson.objects.filter(title__icontains='Débats').first()
    if b2_debats:
        pdf_content = b"%PDF-1.4\n%..."
        r1 = LessonResource(
            video=b2_debats,
            title='Advanced Vocabulary List',
            resource_type='PDF',
            order_index=1
        )
        r1.file.save('advanced_vocab.pdf', ContentFile(pdf_content))

    print("Resources population complete!")

if __name__ == "__main__":
    populate_resources()
