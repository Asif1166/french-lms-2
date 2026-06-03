# French Learning Platform (A1-B2)

A comprehensive Django-based French language learning platform aligned with CEFR levels (A1, A2, B1, B2) and inspired by DELF/DALF exam patterns.

## Features

- **CEFR-Aligned Learning Paths**: Structured courses for A1, A2, B1, and B2 levels
- **Chapter-wise Video Lessons**: Organized learning content with descriptions and exercises
- **Comprehensive Question System**: Multiple question types including:
  - Listening: MCQ, True/False, Fill in the blanks
  - Reading: Matching, Information extraction, Yes/No/Not Mentioned
  - Writing: Email writing, Short paragraph, Opinion-based text
  - Speaking: Role-play, Image description, Topic monologue
- **Mock Exam Module**: Full DELF-style mock tests with timed sections
- **Payment & Enrollment**: Secure payment gateway integration with access control
- **Progress Tracking**: Video completion, chapter progress, and skill-wise performance

## Technology Stack

- **Backend**: Django 5.2+
- **Database**: PostgreSQL (SQLite for development)
- **Frontend**: Django Templates + Bootstrap 5
- **Payment Gateways**: Stripe, PayPal, SSLCommerz, Razorpay (gateway-agnostic)

## Project Structure

```
french_lms/
├── accounts/          # User management and authentication
├── courses/           # Levels, chapters, videos, courses
├── exams/             # Questions, submissions, mock exams
├── payments/          # Payment transactions and webhooks
├── enrollments/       # Course enrollments and progress tracking
├── dashboard/         # User dashboard
├── templates/         # HTML templates
├── static/            # CSS, JS, images
└── media/             # User uploads and media files
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd french_lms
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   - For development, SQLite is already configured
   - For production, update `settings.py` with PostgreSQL credentials

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Database Models

### Core Models

- **User**: Custom user model with roles (Student, Instructor, Admin)
- **Level**: CEFR levels (A1, A2, B1, B2)
- **Category**: Skill types (Listening, Reading, Writing, Speaking)
- **Chapter**: Chapters within each level
- **VideoLesson**: Video lessons with metadata
- **Question**: Questions with multiple types
- **Option**: Options for MCQ questions
- **Submission**: Student submissions
- **Course**: Course packages for enrollment
- **PaymentTransaction**: Payment records
- **Enrollment**: User course enrollments
- **MockExam**: Mock exam structure
- **Progress Models**: Video and chapter progress tracking

## Question Types

The platform supports various question types:

1. **MCQ_SINGLE**: Single answer multiple choice
2. **MCQ_MULTIPLE**: Multiple answer multiple choice
3. **TRUE_FALSE**: True/False questions
4. **FILL_BLANK**: Fill in the blank questions
5. **MATCHING**: Matching questions
6. **YES_NO_NOT_MENTIONED**: Reading comprehension
7. **INFORMATION_EXTRACTION**: Extract information from text
8. **EMAIL_WRITING**: Email composition tasks
9. **SHORT_PARAGRAPH**: Short writing tasks
10. **OPINION_TEXT**: Opinion-based writing
11. **ROLE_PLAY**: Speaking role-play scenarios
12. **IMAGE_DESCRIPTION**: Image-based speaking tasks
13. **TOPIC_MONOLOGUE**: Monologue speaking tasks

## Access Control

- Users must enroll in courses (via payment) to access content
- Enrollment is checked before:
  - Video playback
  - Question attempts
  - Mock exams
  - Progress tracking

## Payment Integration

The platform supports multiple payment gateways:
- Stripe
- PayPal
- SSLCommerz
- Razorpay

Payment flow:
1. User selects course/level
2. Payment intent created
3. Payment completed via gateway
4. Webhook confirmation
5. Enrollment activated

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
```

### Collecting Static Files
```bash
python manage.py collectstatic
```

## License

This project is for educational purposes. DELF/DALF materials are reference only - original content required.

## Author

French Learning Platform Development Team

