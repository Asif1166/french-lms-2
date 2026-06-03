# Database Design Documentation

## Overview

This document describes the complete database schema for the French Learning Platform (A1-B2).

## Entity Relationship Diagram

```
User (accounts.User)
  ├── PaymentTransaction (payments)
  ├── Enrollment (enrollments)
  ├── Submission (exams)
  ├── VideoProgress (enrollments)
  ├── ChapterProgress (enrollments)
  └── MockExamAttempt (exams)

Level (courses.Level)
  ├── Chapter (courses.Chapter)
  │     └── VideoLesson (courses.VideoLesson)
  │           └── Question (exams.Question)
  ├── Course (courses.Course)
  └── Question (exams.Question)

Category (courses.Category)
  ├── VideoLesson (courses.VideoLesson)
  └── MockExamSection (exams.MockExamSection)

Course (courses.Course)
  ├── PaymentTransaction (payments)
  └── Enrollment (enrollments)

Question (exams.Question)
  ├── Option (exams.Option)
  ├── Submission (exams.Submission)
  └── MockExamQuestion (exams.MockExamQuestion)

MockExam (exams.MockExam)
  ├── MockExamSection (exams.MockExamSection)
  │     └── MockExamQuestion (exams.MockExamQuestion)
  └── MockExamAttempt (exams.MockExamAttempt)

PaymentTransaction (payments.PaymentTransaction)
  └── Enrollment (enrollments.Enrollment)
```

## Detailed Model Specifications

### 1. User Model (accounts.User)

**Purpose**: Custom user model with role-based access control

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `email` (Unique): User email address (used as username)
- `username`: Django username field
- `password`: Hashed password
- `role`: Choices - STUDENT, INSTRUCTOR, ADMIN
- `phone`: Optional phone number
- `profile_picture`: Optional profile image
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

**Relationships**:
- One-to-Many: PaymentTransaction, Enrollment, Submission, VideoProgress, ChapterProgress, MockExamAttempt

---

### 2. Level Model (courses.Level)

**Purpose**: Represents CEFR levels (A1, A2, B1, B2)

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `code`: Choices - A1, A2, B1, B2 (Unique)
- `title`: Level title
- `description`: Detailed description
- `order_index`: Display order
- `is_active`: Active status
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

**Relationships**:
- One-to-Many: Chapter, Course, Question

---

### 3. Category Model (courses.Category)

**Purpose**: Skill categories (Listening, Reading, Writing, Speaking)

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `name`: Choices - LISTENING, READING, WRITING, SPEAKING (Unique)
- `description`: Category description
- `icon`: Icon identifier
- `order_index`: Display order

**Relationships**:
- One-to-Many: VideoLesson, MockExamSection

---

### 4. Chapter Model (courses.Chapter)

**Purpose**: Chapters within each level

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `level_id` (FK): Reference to Level
- `title`: Chapter title
- `description`: Chapter description
- `objectives`: Learning objectives
- `grammar_focus`: Grammar topics covered
- `vocabulary_list`: Key vocabulary
- `cultural_notes`: Cultural context
- `exam_relevance`: DELF/DALF relevance
- `order_index`: Display order within level
- `is_active`: Active status
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

**Relationships**:
- Many-to-One: Level
- One-to-Many: VideoLesson, ChapterProgress

**Constraints**:
- Unique together: (level, order_index)

---

### 5. VideoLesson Model (courses.VideoLesson)

**Purpose**: Video lessons within chapters

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `chapter_id` (FK): Reference to Chapter
- `category_id` (FK, Optional): Reference to Category
- `title`: Video title
- `description`: Video description
- `learning_goals`: Learning objectives
- `grammar_explanation`: Grammar content
- `vocabulary_explanation`: Vocabulary content
- `example_dialogues`: Example dialogues
- `video_url`: URL to video file
- `duration`: Duration in seconds
- `thumbnail`: Thumbnail image
- `order_index`: Display order
- `is_active`: Active status
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

**Relationships**:
- Many-to-One: Chapter, Category
- One-to-Many: Question, VideoProgress

---

### 6. Course Model (courses.Course)

**Purpose**: Course packages for payment and enrollment

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `name`: Course name
- `description`: Course description
- `level_id` (FK, Optional): Reference to Level (null for full access)
- `price`: Course price (Decimal)
- `currency`: Currency code (default: USD)
- `is_full_access`: Boolean - provides access to all levels
- `duration_months`: Access duration in months (null = lifetime)
- `is_active`: Active status
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

**Relationships**:
- Many-to-One: Level
- One-to-Many: PaymentTransaction, Enrollment

---

### 7. Question Model (exams.Question)

**Purpose**: Questions associated with videos or levels

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `video_id` (FK, Optional): Reference to VideoLesson
- `level_id` (FK, Optional): Reference to Level
- `question_type`: Choices - 13 different types
- `text`: Question text/prompt
- `instruction`: Answering instructions
- `marks`: Points for this question
- `order_index`: Display order
- `is_active`: Active status
- `audio_url`: Audio file URL (for listening questions)
- `passage`: Reading passage (for reading questions)
- `image`: Image file (for image-based questions)
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

**Question Types**:
1. MCQ_SINGLE - Multiple Choice (Single Answer)
2. MCQ_MULTIPLE - Multiple Choice (Multiple Answers)
3. TRUE_FALSE - True / False
4. FILL_BLANK - Fill in the Blank
5. MATCHING - Matching
6. YES_NO_NOT_MENTIONED - Yes / No / Not Mentioned
7. INFORMATION_EXTRACTION - Information Extraction
8. EMAIL_WRITING - Email Writing
9. SHORT_PARAGRAPH - Short Paragraph
10. OPINION_TEXT - Opinion-based Text
11. ROLE_PLAY - Role-play Simulation
12. IMAGE_DESCRIPTION - Image-based Description
13. TOPIC_MONOLOGUE - Topic Monologue

**Relationships**:
- Many-to-One: VideoLesson, Level
- One-to-Many: Option, Submission, MockExamQuestion

---

### 8. Option Model (exams.Option)

**Purpose**: Options for MCQ, True/False, Matching questions

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `question_id` (FK): Reference to Question
- `text`: Option text
- `is_correct`: Boolean - correct answer flag
- `order_index`: Display order
- `match_key`: Key for matching pairs

**Relationships**:
- Many-to-One: Question
- Many-to-Many: Submission (via selected_options)

---

### 9. Submission Model (exams.Submission)

**Purpose**: Student submissions for questions

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `user_id` (FK): Reference to User
- `question_id` (FK): Reference to Question
- `answer_text`: Text answer (for writing/speaking)
- `selected_options`: Many-to-Many with Option
- `score`: Points awarded
- `max_score`: Maximum possible points
- `review_status`: Choices - PENDING, REVIEWED, AUTO_GRADED
- `feedback`: Instructor feedback
- `reviewed_by_id` (FK, Optional): Reference to User (instructor)
- `reviewed_at`: Review timestamp
- `file_upload`: File upload (for speaking/writing)
- `submitted_at`: Submission timestamp
- `updated_at`: Update timestamp

**Relationships**:
- Many-to-One: User, Question
- Many-to-Many: Option

---

### 10. PaymentTransaction Model (payments.PaymentTransaction)

**Purpose**: Payment transactions for course enrollments

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `user_id` (FK): Reference to User
- `course_id` (FK): Reference to Course
- `gateway`: Choices - STRIPE, PAYPAL, SSLCOMMERZ, RAZORPAY
- `transaction_id`: Gateway transaction ID (Unique)
- `amount`: Payment amount (Decimal)
- `currency`: Currency code
- `status`: Choices - PENDING, SUCCESS, FAILED, CANCELLED, REFUNDED
- `gateway_response`: JSON field for gateway response
- `failure_reason`: Reason for failure
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

**Relationships**:
- Many-to-One: User, Course
- One-to-One: Enrollment

---

### 11. Enrollment Model (enrollments.Enrollment)

**Purpose**: Course enrollments created after successful payment

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `user_id` (FK): Reference to User
- `course_id` (FK): Reference to Course
- `payment_transaction_id` (FK, Optional): Reference to PaymentTransaction
- `status`: Choices - ACTIVE, EXPIRED, CANCELLED
- `enrolled_at`: Enrollment timestamp
- `expires_at`: Expiration date (null = lifetime)
- `cancelled_at`: Cancellation timestamp
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

**Relationships**:
- Many-to-One: User, Course, PaymentTransaction

**Constraints**:
- Unique together: (user, course)

**Methods**:
- `is_active()`: Check if enrollment is currently active
- `has_access_to_level(level)`: Check access to specific level

---

### 12. VideoProgress Model (enrollments.VideoProgress)

**Purpose**: Track video watching progress

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `user_id` (FK): Reference to User
- `video_id` (FK): Reference to VideoLesson
- `is_completed`: Completion status
- `watched_duration`: Seconds watched
- `last_watched_at`: Last watch timestamp
- `completed_at`: Completion timestamp

**Relationships**:
- Many-to-One: User, VideoLesson

**Constraints**:
- Unique together: (user, video)

---

### 13. ChapterProgress Model (enrollments.ChapterProgress)

**Purpose**: Track chapter completion

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `user_id` (FK): Reference to User
- `chapter_id` (FK): Reference to Chapter
- `completion_percentage`: Completion percentage (0-100)
- `is_completed`: Completion status
- `completed_at`: Completion timestamp
- `updated_at`: Update timestamp

**Relationships**:
- Many-to-One: User, Chapter

**Constraints**:
- Unique together: (user, chapter)

---

### 14. MockExam Model (exams.MockExam)

**Purpose**: Mock exam structure for a specific level

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `level_id` (FK): Reference to Level
- `title`: Exam title
- `description`: Exam description
- `duration_minutes`: Total duration in minutes
- `total_marks`: Total marks (default: 100)
- `is_active`: Active status
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

**Relationships**:
- Many-to-One: Level
- One-to-Many: MockExamSection, MockExamAttempt

---

### 15. MockExamSection Model (exams.MockExamSection)

**Purpose**: Sections within mock exam (Listening, Reading, Writing, Speaking)

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `exam_id` (FK): Reference to MockExam
- `category_id` (FK): Reference to Category
- `title`: Section title
- `description`: Section description
- `duration_minutes`: Section duration
- `marks`: Section marks (default: 25)
- `order_index`: Display order

**Relationships**:
- Many-to-One: MockExam, Category
- One-to-Many: MockExamQuestion

---

### 16. MockExamQuestion Model (exams.MockExamQuestion)

**Purpose**: Questions in mock exam sections

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `section_id` (FK): Reference to MockExamSection
- `question_id` (FK): Reference to Question
- `order_index`: Display order

**Relationships**:
- Many-to-One: MockExamSection, Question

**Constraints**:
- Unique together: (section, question)

---

### 17. MockExamAttempt Model (exams.MockExamAttempt)

**Purpose**: Student attempt for a mock exam

**Fields**:
- `id` (PK): Auto-incrementing primary key
- `user_id` (FK): Reference to User
- `exam_id` (FK): Reference to MockExam
- `status`: Choices - IN_PROGRESS, COMPLETED, SUBMITTED
- `started_at`: Start timestamp
- `submitted_at`: Submission timestamp
- `total_score`: Total score
- `listening_score`: Listening section score
- `reading_score`: Reading section score
- `writing_score`: Writing section score
- `speaking_score`: Speaking section score

**Relationships**:
- Many-to-One: User, MockExam

---

## Database Indexes

### Primary Keys
All models use auto-incrementing `id` as primary key.

### Foreign Key Indexes
All foreign key fields are automatically indexed by Django.

### Unique Constraints
- User.email
- Level.code
- Category.name
- PaymentTransaction.transaction_id
- Enrollment (user, course)
- VideoProgress (user, video)
- ChapterProgress (user, chapter)
- MockExamQuestion (section, question)

### Composite Unique Constraints
- Chapter (level, order_index)

---

## Access Control Logic

### Enrollment Check
Before accessing any content, the system checks:
1. User is authenticated
2. User has active enrollment for the course
3. Enrollment has not expired (if expires_at is set)
4. For level-specific access: course.level matches requested level OR course.is_full_access is True

### Progress Tracking
- VideoProgress is created/updated when user watches a video
- ChapterProgress is calculated based on completed videos in the chapter
- Completion percentage = (completed videos / total videos) * 100

---

## Question Pattern Design

Questions are designed to look like real exam papers with:
- Clear instructions
- Proper formatting for different question types
- Support for multimedia (audio, images, passages)
- Structured options for MCQ questions
- Separate handling for auto-graded vs. manually graded questions

---

## Notes

- All timestamps use Django's `auto_now_add` and `auto_now`
- Decimal fields use appropriate precision for currency and scores
- File uploads are stored in organized media directories
- JSON fields are used for flexible gateway responses
- Soft deletes can be implemented using `is_active` flags

