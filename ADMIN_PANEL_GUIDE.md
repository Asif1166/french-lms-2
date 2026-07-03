# French LMS — Custom Admin Panel: Step-by-Step Content Entry Guide

> Admin Panel URL: `/panel/`  
> All sections are in the left sidebar. Follow the order below for first-time setup.

---

## Image Size Reference (Quick Lookup)

| Where Used | Field | Recommended Size | Format |
|---|---|---|---|
| Course cover image | `image` | **800 × 450 px** (16:9) | JPG / PNG |
| Video lesson thumbnail | `thumbnail` | **1280 × 720 px** (16:9) | JPG / PNG |
| Question image (Exercise / Mock Exam) | `image` | **900 × 500 px** (landscape) | JPG / PNG |
| Option image (Exercise / Mock Exam) | `file` | **400 × 300 px** | JPG / PNG |
| Instructor / Founder photo | `photo` | **400 × 400 px** (square) | JPG / PNG |
| User profile picture | `profile_picture` | **300 × 300 px** (square) | JPG / PNG |
| Success story / community photo | `photo` | **600 × 400 px** | JPG / PNG |

> **Tips:**
> - Keep file size under **500 KB** for images, under **5 MB** for audio/video files.
> - PNG for images with text or transparent background; JPG for photos.
> - Audio files: **MP3**, max **10 MB**.
> - Resource files (PDFs, docs): **PDF / DOCX**, max **20 MB**.

---

## STEP 1 — Level Codes

> **Sidebar → Courses → Level Codes**

Level Codes are the foundation (e.g., `A1`, `A2`, `B1`, `B2`, `DELF`). Everything links back to these.

1. Click **"Add Level Code"**
2. Fill in:
   - **Code** — Short code, e.g. `A1` (this appears everywhere on the site)
   - **Name** *(optional)* — Full name, e.g. `A1 - Complete Beginner French`
3. Click **Save**
4. Repeat for each level code you need

---

## STEP 2 — Levels

> **Sidebar → Courses → Levels**

A Level belongs to a Level Code and has pricing/description details shown on the site.

1. Click **"Add Level"**
2. Fill in:
   - **Level Code** — Select from dropdown (e.g., `A1`)
   - **Title** — e.g., `Complete Beginner French`
   - **Description** — Shown on the level detail page
   - **Order Index** — Controls sort order (0 = first)
3. Click **Save**

---

## STEP 3 — Courses

> **Sidebar → Courses → Courses**

A Course sits under a Level and groups Chapters together.

1. Click **"Add Course"**
2. Fill in:
   - **Name** — e.g., `French A1 Full Course`
   - **Description** — Short paragraph about the course
   - **Level** — Select the Level this course belongs to
   - **Image** — Course cover image → **800 × 450 px** (JPG/PNG)
   - **Is Full Access** — Check if enrolling in this course gives access to all chapters under the level
3. Click **Save**

---

## STEP 4 — Chapters

> **Sidebar → Courses → Chapters**

Chapters are sections within a Course (e.g., "Greetings", "Numbers", "Colors").

1. Click **"Add Chapter"**
2. Fill in:
   - **Course** — Select the parent Course
   - **Title** — e.g., `Chapter 1: Greetings`
   - **Description** — Short description of what this chapter covers
   - **Order Index** — Controls order within the course (1, 2, 3 …)
3. Click **Save**

---

## STEP 5 — Video Lessons

> **Sidebar → Video Lessons → Add Video Lesson**

Video Lessons are the core content units. Each lesson can have Resources, Word Meanings, and Exercises added inline on the same page.

### 5a. Basic Lesson Info

1. Click **"Add Video Lesson"**
2. Fill in:
   - **Chapter** — Select the parent Chapter
   - **Title** — e.g., `Lesson 1: Bonjour et Salut`
   - **Description** — What students will learn
   - **Video URL** — Paste YouTube / Vimeo URL  
     *OR*
   - **Video File** — Upload a direct video file (MP4 recommended, max 500 MB)
   - **Thumbnail** — Video preview image → **1280 × 720 px** (JPG/PNG)
   - **Order Index** — Controls order within the chapter (1, 2, 3 …)
   - **Is Free** — Check if this lesson is viewable without enrollment

---

### 5b. Lesson Resources (Blue Section)

Resources are downloadable files attached to the lesson (PDFs, worksheets, slides).

1. Scroll to the **"Lesson Resources"** blue section
2. Click **"+ Add Resource"**
3. Fill in:
   - **Title** — e.g., `Vocabulary Sheet - Lesson 1`
   - **File** — Upload PDF/DOCX (max 20 MB)
   - **Order** — Display order
4. Click **"Save Resource"** (saves without leaving the page)
5. Repeat for more resources

---

### 5c. Word Meanings (Green Section)

Word Meanings are vocabulary items with French word, meaning, and optional pronunciation audio.

1. Scroll to the **"Word Meanings"** green section
2. Click **"+ Add Word Meaning"**
3. Fill in:
   - **Word** — The French word, e.g., `Bonjour`
   - **Meaning** — English meaning, e.g., `Hello / Good morning`
   - **Audio File** *(optional)* — Pronunciation audio → MP3, max 10 MB
   - **Order** — Display order
4. Click **"Save Word Meaning"**
5. Repeat for all vocabulary in this lesson

---

### 5d. Exercises (Amber/Orange Section)

Exercises are interactive question sets for the lesson. Each exercise contains multiple questions; each question has options.

1. Scroll to the **"Exercises"** amber section
2. Click **"+ Add Exercise"**
3. Fill in the Exercise card:
   - **Title** — e.g., `Listening Exercise 1`
   - **Type** — Choose: `Reading`, `Listening`, `Writing`, `Speaking`
   - **Context Text** *(optional)* — Reading passage or instructions shown above questions
   - **Audio File** *(optional)* — Listening audio → MP3, max 10 MB
   - **Order** — Display order

4. Inside the Exercise card, click **"+ Add Question"**
5. For each question:
   - **Type** — Choose question type:
     - `MCQ` — Multiple choice (you add custom options below)
     - `True/False` — Auto-creates True & False options (no manual options needed)
     - `Yes/No/Not Mentioned` — Auto-creates 3 options (no manual options needed)
     - `Fill in the Blank` / `Short Answer` / `Essay` — No options needed
   - **Marks** — Points for this question (e.g., `1`)
   - **Order** — Question order
   - **Question Text** — The actual question
   - **Instruction** *(optional)* — Additional hint/instruction
   - **Image** *(optional)* — Image for this question → **900 × 500 px** (JPG/PNG)
   
6. For **MCQ** questions, click **"+ Add Option"**:
   - **Option Text** — The answer choice text
   - **Image** *(optional)* — Option image → **400 × 300 px** (JPG/PNG)
   - **Correct** — Check the box if this is the correct answer
   - Repeat for each option (minimum 2, typically 4)

7. Click **"Save Exercise"** — this saves the exercise, all its questions, and all options in one step

> **Note:** For True/False and Yes/No/Not Mentioned types, options are created automatically — you do NOT need to add them manually.

---

## STEP 6 — Mock Exams

> **Sidebar → Mock Exams → Mock Exams**

Mock Exams simulate real DELF/DALF exam conditions with timed sections.

### 6a. Create Mock Exam

1. Click **"Add Mock Exam"**
2. Fill in:
   - **Title** — e.g., `DELF A1 Mock Exam 1`
   - **Level** — Select the Level this exam is for
   - **Description** — What this exam covers
   - **Duration (minutes)** — Total exam time, e.g., `90`
   - **Is Free** — Check if anyone can take this exam without purchase
   - **Included with Enrollment** — Check if students enrolled in this level's course get free access
   - *(Leave both unchecked for premium-only exams that require package purchase)*
3. Click **Save**

---

### 6b. Add Sections to Mock Exam

> **Sidebar → Mock Exams → Mock Exams → Edit → Sections**

Each exam has sections (e.g., Listening, Reading, Writing, Speaking).

1. Open the Mock Exam (click its name in the list)
2. Scroll to **"Sections"** (blue section)
3. Click **"+ Add Section"**
4. Fill in:
   - **Title** — Must be one of: `Listening`, `Reading`, `Writing`, `Speaking`  
     *(The title is used for scoring — spelling must match)*
   - **Description** *(optional)* — Instructions for this section
   - **Order** — Section order (1, 2, 3, 4)
5. Click **"Save Section"**
6. Repeat for all sections (typically 4)

---

### 6c. Add Questions to a Section

> **In the Section edit page**

1. From the Mock Exam edit page, click **"Edit"** next to a section
2. Scroll to **"Questions"** (amber section)
3. Click **"+ Add Question"**
4. Fill in:
   - **Type** — `MCQ`, `True/False`, `Yes/No/Not Mentioned`, `Fill in the Blank`, `Short Answer`, `Essay`
   - **Marks** — Points for this question
   - **Order** — Question order within the section
   - **Question Text** — The question
   - **Instruction** *(optional)* — Extra guidance
   - **Image** *(optional)* — Question image → **900 × 500 px** (JPG/PNG)
   - **Context Text** *(optional)* — Reading passage above the question

5. For **MCQ** questions, click **"+ Add Option"**:
   - **Option Text** — Answer choice
   - **Image** *(optional)* — Option image → **400 × 300 px** (JPG/PNG)
   - **Correct** — Check for the correct answer
   
6. Click **"Save Question"**

> **Note:** True/False and Yes/No/Not Mentioned options are auto-created — skip the options step for those types.

---

## STEP 7 — Mock Exam Packages

> **Sidebar → Mock Exams → Packages**

Packages are what students purchase to access premium mock exams.

1. Click **"Add Package"**
2. Fill in:
   - **Name** — e.g., `DELF A1 Complete Package`
   - **Level** — Select from LevelCode dropdown (dynamic list)
   - **Price** — Numeric price, e.g., `49.99`
   - **Currency** — e.g., `EUR`
   - **Description** — What's included
   - **Is Popular** — Check to show "Best Value" badge on pricing page
   - **Display Order** — Controls order on pricing page (1 = first)

3. **Add Features** (bullet points shown on pricing card):
   - Click **"+ Add Feature"**
   - **Name** — e.g., `Detailed Answer Explanations`
   - **Icon** *(optional)* — FontAwesome class, e.g., `fas fa-star`
   - Repeat for each feature

4. Click **Save**

> **Linking exams to a package:** After saving the package, go back to each Mock Exam's edit page and verify the Level matches the package's LevelCode — students who purchase the package automatically get access to all exams under that LevelCode.

---

## STEP 8 — Viewing Users, Enrollments & Payments

These are read-only lists to monitor activity.

### Users
> **Sidebar → Users**
- Shows all registered users with email, join date, and active status.

### Enrollments
> **Sidebar → Enrollments**
- Shows which users are enrolled in which course, enrollment date, and whether it's active.

### Payments
> **Sidebar → Payments**
- Shows all payment transactions: user, amount, currency, status (success/pending/failed), and date.

### Mock Exam Submissions
> **Sidebar → Mock Exams → Submissions**
- Shows all exam attempts: user, exam, score, and submission date.

### Mock Exam Purchases
> **Sidebar → Mock Exams → Purchases**
- Shows all package purchases: user, package, amount paid, and purchase date.

---

## Content Entry Order Summary

```
Level Codes  →  Levels  →  Courses  →  Chapters
     ↓
Video Lessons
    ├── Lesson Resources (PDFs, worksheets)
    ├── Word Meanings   (vocabulary + audio)
    └── Exercises
            └── Questions
                    └── Options

Mock Exams
    └── Sections  (Listening / Reading / Writing / Speaking)
            └── Questions
                    └── Options

Mock Exam Packages  (links to Level Codes)
```

---

## Common Mistakes to Avoid

| Mistake | Correct Approach |
|---|---|
| Adding a Chapter before its Course exists | Always create Course first |
| Adding a Video Lesson before its Chapter exists | Always create Chapter first |
| Mock Exam section title spelt wrong | Must be exactly: `Listening`, `Reading`, `Writing`, or `Speaking` |
| Not checking "Correct" on any option | At least ONE option must be marked correct for MCQ |
| Creating a Package with no matching Mock Exam level | Ensure Mock Exam Level matches the Package LevelCode |
| Uploading very large images (>2MB) | Resize to recommended dimensions before uploading |
| Leaving exam neither Free nor Included with Enrollment | Students won't see it unless they purchase a package |
