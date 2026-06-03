import os
import shutil
from django.conf import settings
from courses.models import Level, Category, Chapter, VideoLesson, Course
from exams.models import (
    MockExam, MockExamPackage, PackageFeature, MockExamSection, 
    MockExamQuestion, Question, Option, MockExamPurchase, 
    MockExamAccess, MockExamAttempt, Submission, ExerciseContext
)
from django.db import transaction
from django.core.files import File

@transaction.atomic
def revamp_database():
    print("🗑️ Clearing existing data...")
    # Delete in order to avoid FK issues
    Submission.objects.all().delete()
    MockExamAttempt.objects.all().delete()
    MockExamQuestion.objects.all().delete()
    MockExamSection.objects.all().delete()
    MockExamAccess.objects.all().delete()
    MockExamPurchase.objects.all().delete()
    MockExam.objects.all().delete()
    MockExamPackage.objects.all().delete()
    PackageFeature.objects.all().delete()
    Course.objects.all().delete()
    
    # Exams app specific
    Option.objects.all().delete()
    Question.objects.all().delete()
    ExerciseContext.objects.all().delete()
    
    # Courses app specific
    VideoLesson.objects.all().delete()
    Chapter.objects.all().delete()
    Category.objects.all().delete()
    Level.objects.all().delete()

    print("✅ Data cleared.")

    print("🏗️ Creating Levels...")
    levels_data = [
        ('A1', 'Découverte (Discovery)', 'Perfect for absolute beginners. Learn to introduce yourself and handle basic needs.', 0),
        ('A2', 'Survie (Survival)', 'Intermediate beginner level. Learn to handle routine tasks and social interactions.', 1),
        ('B1', 'Seuil (Threshold)', 'Independent user. Discuss opinions, travel, and professional situations with ease.', 2),
        ('B2', 'Avancé (Advanced)', 'Upper intermediate level. Fluent discussion on complex topics and social issues.', 3),
    ]
    
    level_objs = {}
    for code, title, desc, order in levels_data:
        lvl = Level.objects.create(code=code, title=title, description=desc, order_index=order)
        level_objs[code] = lvl

    print("🏗️ Creating Categories...")
    categories_data = [
        ('LISTENING', 'Compréhension de l\'oral', 'fas fa-headphones', 0),
        ('READING', 'Compréhension des écrits', 'fas fa-book-open', 1),
        ('WRITING', 'Production écrite', 'fas fa-pen-nib', 2),
        ('SPEAKING', 'Production orale', 'fas fa-comments', 3),
    ]
    
    cat_objs = {}
    for name, desc, icon, order in categories_data:
        cat = Category.objects.create(name=name, description=desc, icon=icon, order_index=order)
        cat_objs[name] = cat

    print("🖼️ Setting up Course Images...")
    image_dir = '/home/asif/.gemini/antigravity/brain/52c3512e-0a8c-47d7-bc10-f60e0e6c996f'
    image_map = {
        'A1': 'french_a1_course_v2_1777018297925.png',
        'A2': 'french_a2_course_v2_1777018323469.png',
        'B1': 'french_b1_course_v2_1777018340500.png',
        'B2': 'french_b2_course_v2_1777018357622.png',
    }

    print("🏗️ Creating Courses...")
    courses_data = [
        ('A1 French: The Complete Beginner Course', 'Master the basics of French with our comprehensive A1 program.', 'A1', 49.00),
        ('A2 French: Building Fluency', 'Take your French to the next level with everyday communication skills.', 'A2', 59.00),
        ('B1 French: Confidence & Culture', 'Become an independent French speaker and handle complex situations.', 'B1', 79.00),
        ('B2 French: Professional Mastery', 'Achieve high-level fluency for work, study, and social life.', 'B2', 99.00),
    ]
    
    for name, desc, lvl_code, price in courses_data:
        course = Course.objects.create(
            name=name,
            description=desc,
            level=level_objs[lvl_code],
            price=price,
            currency='USD',
            is_active=True
        )
        
        # Attach image
        img_name = image_map.get(lvl_code)
        if img_name:
            img_path = os.path.join(image_dir, img_name)
            if os.path.exists(img_path):
                with open(img_path, 'rb') as f:
                    course.image.save(img_name, File(f), save=True)

    print("🏗️ Creating Package Features...")
    features = [
        'Full DELF Exam Format',
        'Detailed PDF Solutions',
        'Audio Recordings Included',
        'Instant Score Analysis',
        'Lifetime Access'
    ]
    feature_objs = [PackageFeature.objects.create(name=f) for f in features]

    print("🏗️ Creating Mock Exam Packages...")
    packages_data = [
        ('A1', 'A1 Complete Mock Exam Pack', '5 Full-length DELF A1 Mock Exams with solutions.', 19.99, 5),
        ('A2', 'A2 Success Mock Exam Pack', '5 Comprehensive A2 Mock Exams for exam readiness.', 24.99, 5),
        ('B1', 'B1 Mastery Mock Exam Pack', '10 Intensive B1 Mock Exams with expert feedback.', 34.99, 10),
        ('B2', 'B2 Professional Mock Exam Pack', '10 Advanced B2 Mock Exams for ultimate preparation.', 44.99, 10),
    ]
    
    for lvl_code, name, desc, price, count in packages_data:
        pkg = MockExamPackage.objects.create(
            level=lvl_code,
            name=name,
            description=desc,
            price=price,
            currency='USD',
            exam_count=count,
            is_active=True
        )
        pkg.features.set(feature_objs)
        
        # Create a sample exam for each package
        exam = MockExam.objects.create(
            level=level_objs[lvl_code],
            title=f"{name} - Sample Exam 1",
            description=f"Initial evaluation exam for level {lvl_code}.",
            duration_minutes=90 if lvl_code in ['A1', 'A2'] else 150,
            total_marks=100.0,
            package=pkg
        )
        
        # Create sections for the exam
        for cat_name, cat in cat_objs.items():
            MockExamSection.objects.create(
                exam=exam,
                category=cat,
                title=cat.get_name_display(),
                duration_minutes=20,
                marks=25.0
            )

    print("🏗️ Creating Chapters & Video Lessons...")
    chapters_data = {
        'A1': [
            ('Les Salutations', 'Learn how to greet people and say goodbye.', 'https://www.youtube.com/watch?v=Kk9Y6Zf8q6E'),
            ('Se Présenter', 'Introduce yourself and ask basic questions.', 'https://www.youtube.com/watch?v=pAnu4V4lq3Y'),
        ],
        'A2': [
            ('La Vie Quotidienne', 'Talk about your daily routine and habits.', 'https://www.youtube.com/watch?v=J3-X9_Z_V7c'),
            ('Raconter ses Souvenirs', 'Use the passé composé to tell stories about the past.', 'https://www.youtube.com/watch?v=6Pz_2M-Z0fQ'),
        ],
        'B1': [
            ('Exprimer son Opinion', 'Learn to structure and share your thoughts on topics.', 'https://www.youtube.com/watch?v=Vl8Wz9wGkYs'),
            ('Le Monde du Travail', 'Professional vocabulary and interviewing in French.', 'https://www.youtube.com/watch?v=hZk77_X3M8k'),
        ],
        'B2': [
            ('Débats de Société', 'Engage in complex discussions about social issues.', 'https://www.youtube.com/watch?v=zT10z1M2_W0'),
            ('Techniques d\'Argumentation', 'Master the art of persuasion and debate.', 'https://www.youtube.com/watch?v=V7B8e8uD3j8'),
        ]
    }

    for lvl_code, chapters in chapters_data.items():
        lvl = level_objs[lvl_code]
        for i, (title, desc, video_url) in enumerate(chapters):
            chapter = Chapter.objects.create(
                level=lvl,
                title=title,
                description=desc,
                objectives=f"Master {title} concepts and vocabulary.",
                order_index=i
            )
            
            # Create a sample video for each chapter
            VideoLesson.objects.create(
                chapter=chapter,
                category=cat_objs['LISTENING'], # Default to listening
                title=f"Lesson: {title}",
                description=f"Deep dive into {title}.",
                learning_goals="Understand core structures and pronunciation.",
                video_url=video_url,
                duration=300, # 5 minutes
                order_index=0
            )

    print("🚀 Database revamp complete!")

print("🏁 Starting database revamp...")
revamp_database()
