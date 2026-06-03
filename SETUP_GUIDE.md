# Setup Guide - French Learning Platform

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Populate Initial Data

```bash
python manage.py init_data
```

This will create:
- CEFR Levels: A1, A2, B1, B2
- Skill Categories: Listening, Reading, Writing, Speaking

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Configure Stripe (Optional)

Add your Stripe keys to `settings.py`:

```python
STRIPE_PUBLIC_KEY = 'pk_test_...'
STRIPE_SECRET_KEY = 'sk_test_...'
STRIPE_WEBHOOK_SECRET = 'whsec_...'
```

Or set them as environment variables:

```bash
export STRIPE_PUBLIC_KEY='pk_test_...'
export STRIPE_SECRET_KEY='sk_test_...'
export STRIPE_WEBHOOK_SECRET='whsec_...'
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Admin Panel

Access the admin panel at: http://127.0.0.1:8000/admin

From here you can:
- Create Levels, Chapters, Videos
- Create Questions with different types
- Create Courses for enrollment
- Manage Users
- Review Submissions

## Creating Content

### Step 1: Create a Level
1. Go to Admin → Courses → Levels
2. Add a new level (A1, A2, B1, or B2)

### Step 2: Create a Chapter
1. Go to Admin → Courses → Chapters
2. Select the level
3. Add chapter details (title, description, objectives, etc.)

### Step 3: Create Video Lessons
1. Go to Admin → Courses → Video Lessons
2. Select the chapter
3. Add video URL (YouTube, Vimeo, or direct link)
4. Add description, learning goals, etc.

### Step 4: Create Questions
1. Go to Admin → Exams → Questions
2. Select the video or level
3. Choose question type
4. Add question text and options (for MCQ)
5. For listening questions, add audio_url
6. For reading questions, add passage
7. For image questions, upload image

### Step 5: Create a Course
1. Go to Admin → Courses → Courses
2. Add course name and description
3. Set price and currency
4. Select level (or leave null for full access)
5. Set duration (or null for lifetime)

## Question Types

The platform supports 13 question types:

### Listening
- **MCQ_SINGLE**: Single answer multiple choice
- **MCQ_MULTIPLE**: Multiple answer multiple choice
- **TRUE_FALSE**: True/False questions
- **FILL_BLANK**: Fill in the blank

### Reading
- **MATCHING**: Matching questions
- **YES_NO_NOT_MENTIONED**: Yes/No/Not Mentioned
- **INFORMATION_EXTRACTION**: Extract information

### Writing
- **EMAIL_WRITING**: Email composition
- **SHORT_PARAGRAPH**: Short paragraph writing
- **OPINION_TEXT**: Opinion-based writing

### Speaking
- **ROLE_PLAY**: Role-play simulation
- **IMAGE_DESCRIPTION**: Image description
- **TOPIC_MONOLOGUE**: Topic monologue

## User Roles

- **STUDENT**: Can enroll, watch videos, attempt questions
- **INSTRUCTOR**: Can review submissions, grade writing/speaking
- **ADMIN**: Full access to all features

## Payment Flow

1. User browses courses
2. User clicks "Enroll Now"
3. Payment page with Stripe integration
4. After successful payment, enrollment is created
5. User can access course content

## Testing Stripe

Use Stripe test cards:
- Success: `4242 4242 4242 4242`
- Decline: `4000 0000 0000 0002`

## Features Implemented

✅ User authentication (login, register, logout)
✅ Course browsing and enrollment
✅ Video player with progress tracking
✅ Question system with 13 question types
✅ Question paper-like UI design
✅ Auto-grading for MCQ questions
✅ Manual grading for writing/speaking
✅ Stripe payment integration
✅ Progress tracking (video and chapter)
✅ Instructor submission review
✅ Mock exam structure
✅ Access control based on enrollment

## Next Steps

1. Add more content (videos, questions)
2. Configure Stripe webhook endpoint
3. Customize templates and styling
4. Add email notifications
5. Implement certificate generation
6. Add analytics and reporting

## Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic
```

### Database issues
```bash
python manage.py makemigrations
python manage.py migrate
```

### Stripe not working
- Check if keys are set in settings.py
- Verify webhook endpoint is accessible
- Check Stripe dashboard for events

## Support

For issues or questions, check the documentation or contact the development team.

