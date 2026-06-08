"""
Management command to populate initial data:
- CEFR Levels (A1, A2, B1, B2)
- Categories (Listening, Reading, Writing, Speaking)
"""
from django.core.management.base import BaseCommand
from courses.models import Level, Category, LevelCode


class Command(BaseCommand):
    help = 'Populate initial data: Levels and Categories'

    def handle(self, *args, **options):
        self.stdout.write('Creating CEFR Levels...')
        
        # Create Levels
        levels_data = [
            {
                'code': 'A1',
                'title': 'A1 - Beginner',
                'description': 'Basic communication skills. Can understand and use familiar everyday expressions and very basic phrases aimed at the satisfaction of needs of a concrete type.',
                'order_index': 1
            },
            {
                'code': 'A2',
                'title': 'A2 - Elementary',
                'description': 'Can understand sentences and frequently used expressions related to areas of most immediate relevance. Can communicate in simple and routine tasks.',
                'order_index': 2
            },
            {
                'code': 'B1',
                'title': 'B1 - Intermediate',
                'description': 'Can understand the main points of clear standard input on familiar matters. Can produce simple connected text on topics of personal interest.',
                'order_index': 3
            },
            {
                'code': 'B2',
                'title': 'B2 - Upper Intermediate',
                'description': 'Can understand the main ideas of complex text on both concrete and abstract topics. Can interact with a degree of fluency and spontaneity.',
                'order_index': 4
            }
        ]
        
        for level_data in levels_data:
            level_code_obj, _ = LevelCode.objects.get_or_create(code=level_data['code'])
            defaults = level_data.copy()
            if 'code' in defaults:
                del defaults['code']
            defaults['level_code'] = level_code_obj

            level, created = Level.objects.get_or_create(
                level_code=level_code_obj,
                defaults=defaults
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created level: {level.code}'))
            else:
                self.stdout.write(self.style.WARNING(f'Level {level.code} already exists'))
        
        self.stdout.write('\nCreating Skill Categories...')
        
        # Create Categories
        categories_data = [
            {
                'name': 'LISTENING',
                'description': 'Compréhension de l\'oral - Listening comprehension skills',
                'icon': 'fas fa-headphones',
                'order_index': 1
            },
            {
                'name': 'READING',
                'description': 'Compréhension des écrits - Reading comprehension skills',
                'icon': 'fas fa-book',
                'order_index': 2
            },
            {
                'name': 'WRITING',
                'description': 'Production écrite - Written production skills',
                'icon': 'fas fa-pen',
                'order_index': 3
            },
            {
                'name': 'SPEAKING',
                'description': 'Production orale - Oral production skills',
                'icon': 'fas fa-microphone',
                'order_index': 4
            }
        ]
        
        for category_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults=category_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.get_name_display()}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category {category.get_name_display()} already exists'))
        
        self.stdout.write(self.style.SUCCESS('\nInitial data populated successfully!'))

