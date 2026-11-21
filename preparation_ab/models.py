from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    DEPARTMENT_CHOICES = (
        ('CSE', 'Computer Science & Engineering'),
        ('IT', 'Information Technology'),
        ('ECE', 'Electronics & Communication Engineering'),
        ('EEE', 'Electrical & Electronics Engineering'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('AI_DS', 'AI & Data Science'),
        ('Other', 'Other'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    year_of_passing = models.IntegerField(blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # New Fields for Student Profile
    bio = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Enter skills separated by commas")
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Category(models.Model):
    """Assessment categories like Quantitative Aptitude, Logical Reasoning, etc."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    time_per_question = models.IntegerField(default=60, help_text="Seconds allowed per question")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Question(models.Model):
    """Multiple choice questions for assessments."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    is_ai_generated = models.BooleanField(default=False)
    generated_for_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_questions')

    def __str__(self):
        return f"{self.category.name}: {self.text[:50]}..."


class AssessmentAttempt(models.Model):
    """Result of an assessment attempt by a student."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='assessment_attempts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    time_taken_seconds = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category.name} ({self.score}/{self.total_questions})"

    class Meta:
        ordering = ['-completed_at']


class Recommendation(models.Model):
    """Personalized career or skill recommendations for a student."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recommendations')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rec for {self.user.username}: {self.title}"


# RESUME UPLOAD

def resume_upload_path(instance, filename):
    """Store each user's resumes in their own subfolder."""
    return f'resumes/user_{instance.user.id}/{filename}'
 
 
class ResumeUpload(models.Model):
    user              = models.ForeignKey(
                            CustomUser,
                            on_delete=models.CASCADE,
                            related_name='resumes'
                        )
    file              = models.FileField(upload_to=resume_upload_path)
    original_filename = models.CharField(max_length=255)
    uploaded_at       = models.DateTimeField(auto_now_add=True)
 
    # Optional: store parsed analysis score for dashboard display
    overall_score     = models.IntegerField(blank=True, null=True)
    analysis_json     = models.JSONField(blank=True, null=True)
 
    class Meta:
        ordering = ['-uploaded_at']
 
    def __str__(self):
        return f"{self.user.username} — {self.original_filename} ({self.uploaded_at:%Y-%m-%d})"
 
    @property
    def file_extension(self):
        return self.original_filename.rsplit('.', 1)[-1].lower() if '.' in self.original_filename else ''


# MOCK INTERVIEW MODULE

class InterviewQuestion(models.Model):
    ROUND_CHOICES = (
        ('HR', 'HR Round'),
        ('Technical', 'Technical Round'),
    )
    round_type = models.CharField(max_length=20, choices=ROUND_CHOICES)
    text = models.TextField()

    def __str__(self):
        return f"{self.round_type}: {self.text[:50]}..."


class MockInterviewSession(models.Model):
    STATUS_CHOICES = (
        ('Completed', 'Completed'),
        ('Failed', 'Failed (Too many interruptions)'),
        ('In Progress', 'In Progress'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='interview_sessions')
    round_type = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Progress')
    title = models.CharField(max_length=200, default='Untitled Session')
    user_notes = models.TextField(blank=True, null=True)
    warnings = models.IntegerField(default=0)
    feedback = models.TextField(blank=True, null=True)
    score = models.IntegerField(default=0)
    
    # Performance Metrics
    wpm = models.IntegerField(default=0)
    filler_count = models.IntegerField(default=0)
    confidence_score = models.IntegerField(default=0)
    transcript = models.TextField(blank=True, null=True)
    recording = models.FileField(upload_to='interview_recordings/', null=True, blank=True)
    strengths = models.TextField(blank=True, null=True)
    weaknesses = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.round_type} ({self.status})"


# ─────────────────────────────────────
# CODING TEST MODULE
# ─────────────────────────────────────

class CodingProblem(models.Model):
    DIFFICULTY_CHOICES = (
        ('Basic', 'Basic'),
        ('Intermediate', 'Intermediate'),
    )
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Full problem statement with constraints")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Basic')
    company_tag = models.CharField(max_length=100, help_text="e.g. Infosys, TCS, Accenture")
    time_limit_minutes = models.IntegerField(default=30)
    sample_input = models.TextField(blank=True)
    sample_output = models.TextField(blank=True)
    test_cases = models.JSONField(default=list, help_text="List of {input, expected_output} objects")
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.company_tag}] {self.title} ({self.difficulty})"

    class Meta:
        ordering = ['company_tag', 'difficulty', 'title']


class CodingSubmission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='coding_submissions')
    problem = models.ForeignKey(CodingProblem, on_delete=models.CASCADE, related_name='submissions')
    title = models.CharField(max_length=200, default='Untitled Submission')
    user_notes = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=30)
    code = models.TextField()
    score = models.IntegerField(default=0)
    evaluation_status = models.CharField(max_length=20, default='completed')
    test_cases_passed = models.IntegerField(default=0)
    total_test_cases = models.IntegerField(default=0)
    time_taken_seconds = models.IntegerField(default=0)
    ai_feedback = models.TextField(blank=True)
    corrected_code = models.TextField(blank=True, default='')
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    improvement_tips = models.JSONField(default=list)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.problem.title} ({self.language}, {self.score}%)"

    class Meta:
        ordering = ['-submitted_at']