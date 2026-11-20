import traceback
from .models import CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import (
    ResumeUpload, Category, Question, AssessmentAttempt, Recommendation,
    InterviewQuestion, MockInterviewSession, CodingProblem, CodingSubmission
)
from .forms import (
    RegisterForm, LoginForm, ProfileUpdateForm, AssessmentForm,
    MockInterviewUpdateForm, CodingSubmissionUpdateForm
)


import json
import random
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from google import genai
from pypdf import PdfReader
import docx
import os
from dotenv import load_dotenv
load_dotenv()
import base64
from io import BytesIO
try:
    import openai
    _openai_available = True
except ImportError:
    openai = None
    _openai_available = False
    print("WARNING: openai not installed.")

# Optional heavy dependencies â€” server starts fine without them
try:
    import cv2
except ImportError:
    cv2 = None
    print("WARNING: cv2 not installed. Camera features disabled.")

try:
    import numpy as np
except ImportError:
    np = None
    print("WARNING: numpy not installed.")

try:
    from ultralytics import YOLO
    _yolo_available = True
except ImportError:
    YOLO = None
    _yolo_available = False
    print("WARNING: ultralytics not installed. YOLO proctoring disabled.")

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
    print("WARNING: pyttsx3 not installed. TTS disabled.")

try:
    from gtts import gTTS
except ImportError:
    gTTS = None
    print("WARNING: gtts not installed. gTTS disabled.")

# Initialize OpenAI Client
if _openai_available:
   
    openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    openai_client = None

# Initialize Gemini Client

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# Model definitions
GEMINI_MODEL_PRO = 'gemini-2.5-pro'
GEMINI_MODEL_FLASH = 'gemini-2.5-flash'

# Load YOLOv8 for server-side proctoring (cached)
yolo_model = None
if _yolo_available:
    try:
        yolo_model = YOLO('yolov8n.pt')
    except Exception as e:
        print(f"YOLO Load Warning: {e}")
        yolo_model = None


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# HOME
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def home(request):
    return render(request, 'preparation_ab/home.html')


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# AUTH
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('dashboard')
            else:
                # Check if user exists to provide specific feedback
                if not CustomUser.objects.filter(username=username).exists():
                    messages.error(request, 'User ID does not exist. Please create a new account.')
                else:
                    messages.error(request, 'Invalid password. Please try again.')
        else:
            # If form errors exist (like recaptcha)
            for field in form:
                for error in field.errors:
                    messages.error(request, error)
            for error in form.non_field_errors():
                messages.error(request, error)
    else:
        form = LoginForm()

    return render(request, 'preparation_ab/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome aboard.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()

    return render(request, 'preparation_ab/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# DASHBOARD
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required(login_url='login')
def dashboard_view(request):
    latest_resume = ResumeUpload.objects.filter(
        user=request.user
    ).order_by('-uploaded_at').first()

    return render(request, 'preparation_ab/dashboard.html', {
        'user': request.user,
        'latest_resume': latest_resume,
    })


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# PROFILE CRUD
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required(login_url='login')
def profile_view(request):
    """View the student profile."""
    return render(request, 'preparation_ab/profile.html', {'user': request.user})


@login_required(login_url='login')
def profile_edit_view(request):
    """Update profile details and profile picture."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'preparation_ab/profile_edit.html', {'form': form})


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# RESUME UPLOAD & ANALYSIS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required(login_url='login')
def resume_upload_view(request):
    """
    Handles resume upload, extracts text, and performs real-time AI analysis using Gemini.
    """
    analysis = None

    if request.method == 'POST':
        resume_file = request.FILES.get('resume')

        if not resume_file:
            messages.error(request, 'No file selected. Please choose your resume.')
            return redirect('resume_upload')

        # File type check
        ext = resume_file.name.lower().split('.')[-1]
        if ext not in ['pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg']:
            messages.error(request, 'Unsupported format. Please upload PDF, DOCX, or Image (PNG, JPG).')
            return redirect('resume_upload')

        # Size check â€” 5 MB
        if resume_file.size > 5 * 1024 * 1024:
            messages.error(request, 'File too large. Maximum size is 5 MB.')
            return redirect('resume_upload')

        # --- TEXT EXTRACTION ---
        resume_text = ""
        try:
            if ext == 'pdf':
                reader = PdfReader(resume_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        resume_text += text + "\n"
            elif ext == 'docx':
                doc = docx.Document(resume_file)
                for para in doc.paragraphs:
                    resume_text += para.text + "\n"
            elif ext == 'doc':
                messages.error(request, 'The .doc format is outdated. Please save it as .docx or .pdf and try again.')
                return redirect('resume_upload')
        except Exception as e:
            messages.error(request, f"Error extracting text: {str(e)}")
            return redirect('resume_upload')

        # FALLBACK: If extraction failed (e.g. image-based PDF), use Gemini 1.5 Flash to extract text
        if not resume_text.strip():
            try:
                # Reset file pointer
                resume_file.seek(0)
                file_data = resume_file.read()
                
                if ext == 'pdf':
                    # Gemini 1.5 Flash can process PDF bytes directly for OCR
                    response = gemini_client.models.generate_content(
                        model=GEMINI_MODEL_FLASH,
                        contents=[
                            "Extract all text from this resume PDF. Maintain the structure and content accurately.",
                            {'mime_type': 'application/pdf', 'data': file_data}
                        ]
                    )
                    resume_text = response.text
                elif ext in ['png', 'jpg', 'jpeg']:
                    # Handle image formats
                    mime_type = 'image/png' if ext == 'png' else 'image/jpeg'
                    response = gemini_client.models.generate_content(
                        model=GEMINI_MODEL_FLASH,
                        contents=[
                            "Extract all text from this resume image. Maintain the structure and content accurately.",
                            {'mime_type': mime_type, 'data': file_data}
                        ]
                    )
                    resume_text = response.text
                
                # If still empty after AI attempt
                if not resume_text.strip():
                    messages.error(request, "Could not extract text from the resume. Please ensure the file is not corrupted or password-protected.")
                    return redirect('resume_upload')
            except Exception as ai_e:
                print(f"AI Fallback Error: {str(ai_e)}")
                messages.error(request, "Could not extract text from the resume. Please check the file format.")
                return redirect('resume_upload')


        # Save to database
        try:
            resume_file.seek(0)
            upload = ResumeUpload.objects.create(
                user=request.user,
                file=resume_file,
                original_filename=resume_file.name,
            )
        except Exception:
            traceback.print_exc()
            messages.error(request, "Resume upload failed. Please try again.")
            return redirect('resume_upload')
                

        # --- OPENAI ANALYSIS ---
        try:
            prompt = f"""
            Analyze the following resume text and provide a highly structured JSON response.
            IMPORTANT: This is a real-time analysis for the file: "{resume_file.name}". 
            Be extremely specific to the content provided below. Do not use generic placeholders.
            
            Break down the resume into these specific sections:
            1. personal_info: (name, email, phone, location, linkedin, github)
            2. executive_summary: (A brief 2-3 sentence professional summary)
            3. qualifications: (array of objects with 'degree', 'institution', 'year', 'score')
            4. experience: (array of objects with 'role', 'company', 'duration', 'description')
            5. skills_assessment: {{
                "technical_skills": ["existing skills found"],
                "recommended_skills": ["skills they should learn for their target roles"]
            }}
            6. certifications: (array of strings)
            7. ats_metrics: {{
                "overall_score": 0-100,
                "breakdown": [
                    {{"label": "Skills Match", "score": 0-100}},
                    {{"label": "Experience", "score": 0-100}},
                    {{"label": "Education", "score": 0-100}},
                    {{"label": "Formatting", "score": 0-100}},
                    {{"label": "Keywords", "score": 0-100}}
                ],
                "missing_keywords": ["important keywords for ATS"]
            }}
            8. suggestions: ["detailed improvement tips"]
            9. recommended_roles: [{{"title": "string", "match": 0-100}}]

            Resume Text:
            {resume_text}
            
            Respond with valid JSON only.
            """
            
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL_FLASH,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "system_instruction": (
                        "You are a professional ATS resume reviewer. "
                        "Return valid JSON matching the requested structure. "
                        "Base all scores and recommendations on the actual resume content. "
                        "Do not invent personal information, experience, or qualifications."
                    ),
                },
            )

            res_content = response.text
            if not res_content:
                raise ValueError("Gemini returned an empty response")
            
            analysis_data = json.loads(res_content.strip())
            
            # Format for the template with safety checks
            ats = analysis_data.get('ats_metrics', {})
            skills_data = analysis_data.get('skills_assessment', {})
            overall_score = ats.get('overall_score') or 0
            
            analysis = {
                'personal_info': analysis_data.get('personal_info', {}),
                'summary': analysis_data.get('executive_summary', ''),
                'qualifications': analysis_data.get('qualifications', []),
                'experience': analysis_data.get('experience', []),
                'certifications': analysis_data.get('certifications', []),
                'overall_score': overall_score,
                'score_dash': round(float(overall_score) / 100 * 377, 1),
                'breakdown': ats.get('breakdown', []),
                'skills': skills_data.get('technical_skills', []),
                'recommended_skills': skills_data.get('recommended_skills', []),
                'missing_keywords': ats.get('missing_keywords', []),
                'suggestions': analysis_data.get('suggestions', []),
                'recommended_roles': analysis_data.get('recommended_roles', []),
            }
            
            # Save analysis to database for persistence
            upload.overall_score = analysis['overall_score']
            upload.analysis_json = analysis
            upload.save()
            
            messages.success(request, f'Resume "{resume_file.name}" analyzed successfully!')
        except Exception as e:
            print(f"AI ERROR: {str(e)}") # Log to server console
            traceback.print_exc()
            messages.error(request, f"AI Analysis failed: {str(e)}")
            analysis = None

    # Fetch recent uploads to show history
    recent_uploads = ResumeUpload.objects.filter(user=request.user).order_by('-uploaded_at')[:5]

    return render(request, 'preparation_ab/resume_upload.html', {
        'user': request.user,
        'analysis': analysis,
        'recent_uploads': recent_uploads,
    })


@login_required(login_url='login')
def delete_resume(request, resume_id):
    """Deletes a specific resume upload via POST/AJAX."""
    print(f"DEBUG: Delete resume called for {resume_id}, method: {request.method}")
    if request.method == 'POST':
        try:
            resume = get_object_or_404(ResumeUpload, id=resume_id, user=request.user)
            filename = resume.original_filename
            
            # Delete the actual file from storage
            if resume.file and os.path.isfile(resume.file.path):
                try:
                    os.remove(resume.file.path)
                except Exception as e:
                    print(f"FILE DELETE ERROR: {str(e)}")
            
            resume.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': f'Resume "{filename}" deleted.'})
            
            messages.success(request, f'Resume "{filename}" deleted successfully.')
        except Exception as e:
            print(f"DELETE ERROR: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Error deleting resume: {str(e)}')
    
    return redirect('resume_upload')


def get_mock_analysis():
    """Helper for fallback or development."""
    overall_score = 74
    return {
        'personal_info': {'name': 'John Doe', 'email': 'john@example.com'},
        'summary': 'Passionate software engineer with 3+ years of experience in web development.',
        'qualifications': [{'degree': 'B.Tech CS', 'institution': 'Example University', 'year': '2022'}],
        'experience': [{'role': 'Junior Developer', 'company': 'Tech Corp', 'duration': '2 years'}],
        'certifications': ['AWS Cloud Practitioner'],
        'overall_score': overall_score,
        'score_dash': round(overall_score / 100 * 314, 1),
        'breakdown': [
            {'label': 'Skills Match', 'score': 80},
            {'label': 'Experience',   'score': 70},
            {'label': 'Education',    'score': 90},
            {'label': 'Formatting',   'score': 65},
            {'label': 'Keywords',     'score': 60},
        ],
        'skills': ['Python', 'Django', 'SQL', 'REST APIs', 'Git', 'Linux'],
        'recommended_skills': ['Docker', 'AWS', 'CI/CD'],
        'missing_keywords': ['Docker', 'AWS', 'CI/CD', 'Kubernetes', 'Agile'],
        'suggestions': [
            'Add a concise professional summary at the top of your resume.',
            'Quantify achievements â€” use numbers and percentages wherever possible.',
            'Include Docker and cloud technologies to improve your ATS score.',
        ],
        'recommended_roles': [
            {'title': 'Backend Developer',        'match': 85},
            {'title': 'Full Stack Engineer',      'match': 78},
        ],
    }


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ASSESSMENT MODULE (TIMED + AI QUESTIONS)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required(login_url='login')
def assessment_list_view(request):
    """List categorized assessments with time info."""
    categories = Category.objects.all()
    category_data = []
    for cat in categories:
        question_count = cat.questions.filter(is_ai_generated=False).count()
        # Default to 20 questions if we have enough, otherwise use what's available
        num_questions = min(question_count, 20) if question_count > 0 else 20
        total_time = num_questions * cat.time_per_question
        category_data.append({
            'category': cat,
            'num_questions': num_questions,
            'total_time_minutes': total_time // 60,
        })
    return render(request, 'preparation_ab/assessment_list.html', {'category_data': category_data})


def _generate_ai_questions(category, user, count=20):
    """
    Use OpenAI to generate fresh MCQ questions for a category.
    Returns a list of Question objects (already saved to DB).
    """
    try:
        prompt = f"""
        Generate {count} unique multiple-choice questions for the aptitude category: "{category.name}".
        {"Description: " + category.description if category.description else ""}
        
        These are for a placement preparation platform used by Indian engineering students.
        Mix difficulty levels: some easy, some medium, some tricky.
        
        Respond ONLY with a valid JSON object containing:
        {{
            "questions": [
                {{
                    "text": "The question text",
                    "option_a": "Option A text",
                    "option_b": "Option B text", 
                    "option_c": "Option C text",
                    "option_d": "Option D text",
                    "correct_answer": "A"  // Must be A, B, C, or D
                }}
            ]
        }}
        
        IMPORTANT: Make sure questions are diverse, not repetitive, and test real aptitude skills.
        """
        
        # Use OpenAI for question generation
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a test creator. Return strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        res_content = response.choices[0].message.content.strip()
        data = json.loads(res_content)
        
        generated_questions = []
        for q_data in data.get('questions', [])[:count]:
            q = Question.objects.create(
                category=category,
                text=q_data['text'],
                option_a=q_data['option_a'],
                option_b=q_data['option_b'],
                option_c=q_data['option_c'],
                option_d=q_data['option_d'],
                correct_answer=q_data['correct_answer'].upper(),
                is_ai_generated=True,
                generated_for_user=user,
            )
            generated_questions.append(q)
        
        return generated_questions
    except Exception as e:
        print(f"AI Question Generation failed: {e}")
        return None


@login_required(login_url='login')
def take_assessment_view(request, category_id):
    """The interactive timed test interface with AI-generated fresh questions."""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        # Retrieve the question IDs that were served (passed via hidden field)
        question_ids = request.POST.get('question_ids', '')
        if question_ids:
            q_ids = [int(x) for x in question_ids.split(',') if x.strip()]
            questions = Question.objects.filter(id__in=q_ids)
        else:
            questions = category.questions.all()
        
        time_taken = int(request.POST.get('time_taken', 0))
        
        score = 0
        for q in questions:
            answer = request.POST.get(f'question_{q.id}')
            if answer == q.correct_answer:
                score += 1
        
        attempt = AssessmentAttempt.objects.create(
            user=request.user,
            category=category,
            score=score,
            total_questions=questions.count(),
            time_taken_seconds=time_taken,
        )
        return redirect('assessment_result', attempt_id=attempt.id)
    
    # GET â€” Generate fresh questions
    # Try AI generation first, fallback to DB questions
    num_questions = 20
    questions = _generate_ai_questions(category, request.user, count=num_questions)
    
    if not questions:
        # Fallback: get DB questions, exclude ones this user has already seen via AI
        seen_ids = Question.objects.filter(
            generated_for_user=request.user, category=category
        ).values_list('id', flat=True)
        
        available = list(category.questions.filter(is_ai_generated=False).exclude(id__in=seen_ids))
        if len(available) < num_questions:
            # If not enough unseen, just use all available and shuffle
            available = list(category.questions.filter(is_ai_generated=False))
        
        questions = random.sample(available, min(len(available), num_questions))
    
    total_time_seconds = len(questions) * category.time_per_question
    
    return render(request, 'preparation_ab/take_assessment.html', {
        'category': category,
        'questions': questions,
        'total_time_seconds': total_time_seconds,
        'question_ids': ','.join(str(q.id) for q in questions),
    })


@login_required(login_url='login')
def assessment_result_view(request, attempt_id):
    """Display score and feedback."""
    attempt = AssessmentAttempt.objects.get(id=attempt_id)
    return render(request, 'preparation_ab/assessment_result.html', {'attempt': attempt})


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# RECOMMENDATIONS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
@login_required(login_url='login')
def recommendation_view(request):
    """
    Suggest career paths, jobs, and tests based on profile and test performance using OpenAI.
    """
    attempts = AssessmentAttempt.objects.filter(user=request.user)
    interviews = MockInterviewSession.objects.filter(user=request.user)
    coding_tests = CodingSubmission.objects.filter(user=request.user)
    
    skills = request.user.skills if request.user.skills else ""
    
    # Context for OpenAI
    performance_summary = ""
    for attempt in attempts:
        performance_summary += f"- Assessment ({attempt.category.name}): {attempt.score}/{attempt.total_questions}\n"
    
    for interview in interviews:
        performance_summary += f"- Mock Interview ({interview.round_type}): Score {interview.score}%, Confidence {interview.confidence_score}%, Pace {interview.wpm} WPM\n"
        
    for coding in coding_tests:
        performance_summary += f"- Coding Test ({coding.problem.title}): Score {coding.score}%, Language {coding.language}\n"

    recoms = []

    try:
        prompt = f"""
        Based on the following student profile, assessment performance, and mock interview performance, provide personalized recommendations.
        Skills: {skills}
        Performance History:
        {performance_summary if performance_summary else "No assessments or interviews taken yet."}

        Provide a JSON response with:
        - job_recommendations: array of objects with 'title', 'reason', and 'skill_level' (Entry/Mid/Senior)
        - test_recommendations: array of objects with 'category_name' and 'reason'
        - career_paths: array of objects with 'title' and 'description'

        Respond ONLY with a valid JSON.
        """
        
        # Use OpenAI for recommendations
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a career advisor. Return strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        res_content = response.choices[0].message.content
        recom_data = json.loads(res_content)
        
        # Convert to a flat list for the existing template
        for job in recom_data.get('job_recommendations', []):
            recoms.append({
                "title": f"Job: {job['title']} ({job['skill_level']})",
                "reason": job['reason'],
                "type": "job"
            })
        for test in recom_data.get('test_recommendations', []):
            recoms.append({
                "title": f"Test: {test['category_name']}",
                "reason": test['reason'],
                "type": "test"
            })
        for path in recom_data.get('career_paths', []):
            recoms.append({
                "title": f"Career: {path['title']}",
                "reason": path['description'],
                "type": "path"
            })
    except Exception as e:
        messages.error(request, f"Recommendation AI failed: {str(e)}")
        # Fallback to simple logic
    
    if not recoms:
        # Simple fallback logic
        if any(skill in skills.lower() for skill in ["python", "django", "coding"]):
            recoms.append({
                "title": "Backend Architecture Specialization",
                "reason": "Based on your foundation in Python/Django.",
                "type": "path"
            })
        
        for attempt in attempts:
            if attempt.score / attempt.total_questions > 0.7:
                 recoms.append({
                     "title": f"Advanced {attempt.category.name} Practitioner",
                     "reason": f"Excellent score of {attempt.score}/{attempt.total_questions} achieved.",
                     "type": "path"
                 })
        
        if not recoms:
            recoms.append({
                "title": "Start Your First Assessment",
                "reason": "Complete a test to get personalized career recommendations.",
                "type": "test"
            })

    return render(request, 'preparation_ab/recommendations.html', {'recoms': recoms})


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MOCK INTERVIEW MODULE
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@login_required(login_url='login')
def mock_interview_list(request):
    """Selection page for HR or Technical round."""
    return render(request, 'preparation_ab/mock_interview_list.html')


@login_required(login_url='login')
def mock_interview_session(request, round_type):
    """The interactive interview session with camera and questions."""
    questions = list(InterviewQuestion.objects.filter(round_type=round_type))
    
    # Select 10 random questions or all if less than 10
    total_to_pick = min(len(questions), 10)
    
    if round_type == 'HR':
        # Find "Tell me about yourself"
        starter = next((q for q in questions if "tell me about yourself" in q.text.lower()), None)
        others = [q for q in questions if q != starter]
        selected_questions = random.sample(others, total_to_pick - 1) if others else []
        if starter:
            selected_questions.insert(0, starter)
    else:
        selected_questions = random.sample(questions, total_to_pick) if questions else []
    
    # Prepare JSON for JS
    questions_json = [
        {'id': q.id, 'text': q.text} for q in selected_questions
    ]
    
    return render(request, 'preparation_ab/mock_interview_session.html', {
        'round_type': round_type,
        'questions': selected_questions,
        'questions_json': questions_json,
        'question_count': len(selected_questions)
    })


@csrf_exempt
@login_required(login_url='login')
def process_mock_interview(request):
    """Process the interview result and generate AI feedback."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            round_type = data.get('round_type')
            status = data.get('status') # 'Completed' or 'Failed'
            warnings = data.get('warnings', 0)
            metrics = data.get('metrics', {})
            transcript = data.get('transcript', "")
            
            # --- OPENAI FEEDBACK LOGIC ---
            if status == 'Failed' or not str(transcript or "").strip():
                feedback = "Interview terminated due to multiple interruptions. Please maintain focus and stay within the application window."
                score = 0
            else:
                wpm = metrics.get('wpm', 0)
                confidence = metrics.get('confidence', 0)
                fillers = metrics.get('filler_count', 0)

                # Default fallback values for AI feedback
                ai_data = {
                    "overall_feedback": f"Analyzed WPM: {wpm}, Fillers: {fillers}. Your confidence was {confidence}%.",
                    "strengths": [],
                    "areas_for_improvement": [],
                    "professional_tips": [],
                    "score": 0
                }

                prompt = f"""
                Act as a professional interviewer. Provide detailed feedback for a {round_type} interview based on the transcript and metrics.
                Transcript: {transcript}
                WPM (Pace): {wpm}
                Confidence: {confidence}%
                Filler Words Count: {fillers}
                Warnings (Interruptions): {warnings}

                Provide a JSON response with:
                - overall_feedback (string)
                - strengths (array of strings)
                - areas_for_improvement (array of strings)
                - professional_tips (array of strings)
                - score (0-100)

                Respond ONLY with a valid JSON.
                """

                try:
                    # Use OpenAI for interview feedback
                    response = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a professional interviewer. Return strictly valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        response_format={"type": "json_object"}
                    )
                    res_content = response.choices[0].message.content
                    ai_data = json.loads(res_content)
                    
                    # Construct a readable string for the model's feedback field
                    feedback_parts = [
                        f"Overall: {ai_data.get('overall_feedback', '')}",
                        "\nStrengths:", 
                        *[f"- {s}" for s in ai_data.get('strengths', [])],
                        "\nImprovement:",
                        *[f"- {a}" for a in ai_data.get('areas_for_improvement', [])],
                        "\nTips:",
                        *[f"- {t}" for t in ai_data.get('professional_tips', [])]
                    ]
                    feedback = "\n".join(feedback_parts)
                    score = ai_data.get('score', 0)
                except Exception as e:
                    print(f"INTERVIEW AI FEEDBACK ERROR: {str(e)}")
                    # Fallback already set in ai_data initialization
                    feedback = ai_data.get('overall_feedback', '')
                    score = ai_data.get('score', 0)

            session = MockInterviewSession.objects.create(
                user=request.user,
                round_type=round_type,
                status=status,
                warnings=warnings,
                feedback=feedback,
                score=score,
                wpm=metrics.get('wpm', 0),
                filler_count=metrics.get('filler_count', 0),
                confidence_score=metrics.get('confidence', 0),
                transcript=transcript,
                strengths=json.dumps(ai_data.get('strengths', [])),
                weaknesses=json.dumps(ai_data.get('areas_for_improvement', ai_data.get('weaknesses', [])))
            )
            
            return JsonResponse({'status': 'success', 'session_id': session.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)


@csrf_exempt
@login_required(login_url='login')
def upload_interview_video(request):
    """Save the recorded interview video blob."""
    if request.method == 'POST':
        try:
            session_id = request.POST.get('session_id')
            video_file = request.FILES.get('video')
            
            if not session_id or not video_file:
                return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
            
            session = MockInterviewSession.objects.get(id=session_id, user=request.user)
            session.recording = video_file
            session.save()
            
            print(f"SUCCESS: Video uploaded for Session {session_id}")
            return JsonResponse({'status': 'success', 'message': 'Video saved successfully'})
        except MockInterviewSession.DoesNotExist:
            print(f"ERROR: Session {session_id} not found for upload")
            return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)
        except Exception as e:
            print(f"UPLOAD ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)


@login_required(login_url='login')
def mock_interview_result(request, session_id):
    """Display the results and feedback of an interview session."""
    print(f"DEBUG: Viewing interview result for session {session_id}")
    session = MockInterviewSession.objects.get(id=session_id)
    
    # Parse strengths and weaknesses
    try:
        strengths = json.loads(session.strengths) if session.strengths else []
        weaknesses = json.loads(session.weaknesses) if session.weaknesses else []
    except:
        strengths = []
        weaknesses = []
        
    return render(request, 'preparation_ab/mock_interview_result.html', {
        'session': session,
        'strengths': strengths,
        'weaknesses': weaknesses
    })


@login_required(login_url='login')
def interview_history(request):
    """View to list all past mock interview sessions."""
    sessions = MockInterviewSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'preparation_ab/mock_interview_history.html', {'sessions': sessions})


@login_required(login_url='login')
def delete_mock_interview(request, session_id):
    """Delete a mock interview session and its recording."""
    print(f"DEBUG: Delete mock interview called for {session_id}, method: {request.method}")
    if request.method == 'POST':
        try:
            session = MockInterviewSession.objects.get(id=session_id, user=request.user)
            if session.recording and session.recording.name:
                session.recording.delete()
            session.delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Interview session deleted.'})
            messages.success(request, 'Interview session deleted.')
        except MockInterviewSession.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Session not found.'}, status=404)
            messages.error(request, 'Session not found.')
        except Exception as e:
            print(f"DELETE INTERVIEW ERROR: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Error deleting interview: {str(e)}')
    return redirect('interview_history')


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# CODING TEST MODULE
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

SUPPORTED_LANGUAGES = [
    {'id': 'python', 'name': 'Python', 'icon': 'devicon-plain:python', 'ext': '.py'},
    {'id': 'java', 'name': 'Java', 'icon': 'devicon-plain:java', 'ext': '.java'},
    {'id': 'c', 'name': 'C', 'icon': 'devicon-plain:c', 'ext': '.c'},
    {'id': 'cpp', 'name': 'C++', 'icon': 'devicon-plain:cplusplus', 'ext': '.cpp'},
    {'id': 'javascript', 'name': 'JavaScript', 'icon': 'devicon-plain:javascript', 'ext': '.js'},
    {'id': 'php', 'name': 'PHP', 'icon': 'devicon-plain:php', 'ext': '.php'},
    {'id': 'ruby', 'name': 'Ruby', 'icon': 'devicon-plain:ruby', 'ext': '.rb'},
    {'id': 'go', 'name': 'Go', 'icon': 'devicon-plain:go', 'ext': '.go'},
]

COMPANY_LIST = ['Infosys', 'TCS', 'Accenture', 'Wipro', 'Cognizant', 'HCL']


@login_required(login_url='login')
def coding_test_list(request):
    """Lists available coding problems grouped by company and difficulty."""
    problems = CodingProblem.objects.all()
    
    # Group by company
    company_filter = request.GET.get('company', 'All')
    difficulty_filter = request.GET.get('difficulty', 'All')
    
    if company_filter != 'All':
        problems = problems.filter(company_tag=company_filter)
    if difficulty_filter != 'All':
        problems = problems.filter(difficulty=difficulty_filter)
    
    # Get submission stats for current user
    user_submissions = CodingSubmission.objects.filter(user=request.user)
    solved_problem_ids = set(user_submissions.values_list('problem_id', flat=True))
    
    return render(request, 'preparation_ab/coding_test_list.html', {
        'problems': problems,
        'companies': COMPANY_LIST,
        'languages': SUPPORTED_LANGUAGES,
        'selected_company': company_filter,
        'selected_difficulty': difficulty_filter,
        'solved_ids': solved_problem_ids,
        'total_solved': len(solved_problem_ids),
        'total_problems': CodingProblem.objects.count(),
    })


@login_required(login_url='login')
def coding_test_session(request, problem_id):
    """The active coding IDE page."""
    problem = get_object_or_404(CodingProblem, id=problem_id)
    language = request.GET.get('lang', 'python')
    
    # Get language info
    lang_info = next((l for l in SUPPORTED_LANGUAGES if l['id'] == language), SUPPORTED_LANGUAGES[0])
    
    # Provide boilerplate code per language
    boilerplate = _get_boilerplate(language)
    
    total_time_seconds = problem.time_limit_minutes * 60
    
    return render(request, 'preparation_ab/coding_test_session.html', {
        'problem': problem,
        'language': language,
        'lang_info': lang_info,
        'languages': SUPPORTED_LANGUAGES,
        'boilerplate': boilerplate,
        'total_time_seconds': total_time_seconds,
    })


def _get_boilerplate(language):
    """Return starter code for each supported language."""
    templates = {
        'python': '# Write your solution below\ndef solve():\n    # Read input\n    n = int(input())\n    \n    # Your logic here\n    \n    # Print output\n    print(n)\n\nsolve()',
        'java': 'import java.util.Scanner;\n\npublic class Solution {\n    public static void main(String[] args) {\n        Scanner sc = new Scanner(System.in);\n        int n = sc.nextInt();\n        \n        // Your logic here\n        \n        System.out.println(n);\n    }\n}',
        'c': '#include <stdio.h>\n\nint main() {\n    int n;\n    scanf("%d", &n);\n    \n    // Your logic here\n    \n    printf("%d\\n", n);\n    return 0;\n}',
        'cpp': '#include <iostream>\nusing namespace std;\n\nint main() {\n    int n;\n    cin >> n;\n    \n    // Your logic here\n    \n    cout << n << endl;\n    return 0;\n}',
        'javascript': '// Read input from stdin\nconst readline = require("readline");\nconst rl = readline.createInterface({ input: process.stdin });\n\nrl.on("line", (line) => {\n    const n = parseInt(line);\n    \n    // Your logic here\n    \n    console.log(n);\n});',
        'php': '<?php\n$n = intval(trim(fgets(STDIN)));\n\n// Your logic here\n\necho $n . "\\n";\n?>',
        'ruby': '# Read input\nn = gets.chomp.to_i\n\n# Your logic here\n\nputs n',
        'go': 'package main\n\nimport "fmt"\n\nfunc main() {\n    var n int\n    fmt.Scan(&n)\n    \n    // Your logic here\n    \n    fmt.Println(n)\n}',
    }
    return templates.get(language, '// Write your code here')


@csrf_exempt
@login_required(login_url='login')
def submit_coding_test(request):
    """Evaluate submitted code using OpenAI and return results."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            problem_id = data.get('problem_id')
            language = data.get('language', 'python')
            code = data.get('code', '')
            if not isinstance(code, str) or not code.strip():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please write your code before submitting.'
                }, status=400)
            time_taken = data.get('time_taken_seconds', 0)
            
            problem = get_object_or_404(CodingProblem, id=problem_id)
            
            # --- GEMINI CODE EVALUATION ---
            test_cases_json = json.dumps(problem.test_cases) if problem.test_cases else "[]"
            
            prompt = f"""
            You are a senior technical interviewer and competitive programming judge. 
            Evaluate the following code submission for the problem: "{problem.title}".

            **Problem Details:**
            Description: {problem.description}
            Sample Input: {problem.sample_input}
            Sample Output: {problem.sample_output}
            
            **Hidden Test Cases:**
            {test_cases_json}

            **Submission Info:**
            Language: {language}
            Time Taken: {time_taken} seconds

            **Submitted Code:**
            ```{language}
            {code}
            ```

            **Your Task:**
            1. Mentally execute the code against all test cases.
            2. Check for logic errors, time complexity issues, and language-specific best practices.
            3. Provide a constructive, professional review.
            4. If the solution is incorrect, identify the exact logical or syntax mistakes.
            5. Explain which test cases fail and why. Do not invent successful test results.
            6. Include a corrected working solution in the code_review field.

            **Return a JSON object exactly in this format:**
            {{
                "test_cases_passed": <int: number of passed cases>,
                "total_test_cases": <int: total cases including sample>,
                "score": <int: 0-100 score>,
                "feedback": "Concise summary of performance",
                "strengths": ["list of what they did well"],
                "weaknesses": ["list of errors or inefficiencies"],
                "improvement_tips": ["actionable advice to improve"],
                "code_review": "Line-by-line or section-by-section analysis with code snippets if needed",
                "time_complexity": "e.g., O(n log n)",
                "space_complexity": "e.g., O(n)"
            }}

            Ensure the response is strictly valid JSON.
            """
            
            try:
                response = gemini_client.models.generate_content(
                    model=GEMINI_MODEL_FLASH,
                    contents=prompt,
                    config={
                        "response_mime_type": "application/json",
                        "system_instruction": (
                            "You are a competitive programming judge. "
                            "Evaluate the submitted code carefully. "
                            "Return valid JSON only. "
                            "Do not award points for blank or incorrect solutions. "
                            "Explain specific mistakes and suggest corrected code."
                        ),
                    },
                )

                res_content = response.text
                if not res_content:
                    raise ValueError("Gemini returned an empty response")
                ai_data = json.loads(res_content, strict=False)
                
                submission = CodingSubmission.objects.create(
                    user=request.user,
                    problem=problem,
                    language=language,
                    code=code,
                    score=ai_data.get('score', 0),
                    test_cases_passed=ai_data.get('test_cases_passed', 0),
                    total_test_cases=ai_data.get('total_test_cases', 0),
                    time_taken_seconds=time_taken,
                    ai_feedback=ai_data.get('feedback', '') + "\n\n" + ai_data.get('code_review', ''),
                    strengths=ai_data.get('strengths', []),
                    weaknesses=ai_data.get('weaknesses', []),
                    improvement_tips=ai_data.get('improvement_tips', []),
                )
                
                return JsonResponse({
                    'status': 'success',
                    'submission_id': submission.id,
                })
            except Exception as e:
                # Fallback: save submission with basic evaluation
                submission = CodingSubmission.objects.create(
                    user=request.user,
                    problem=problem,
                    language=language,
                    code=code,
                    score=0,
                    time_taken_seconds=time_taken,
                    ai_feedback=f"AI evaluation temporarily unavailable. Error: {str(e)}",
                    strengths=["Code was submitted successfully"],
                    weaknesses=["Could not perform full AI analysis"],
                    improvement_tips=["Try submitting again later for detailed feedback"],
                )
                return JsonResponse({
                    'status': 'success',
                    'submission_id': submission.id,
                })
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=405)


@login_required(login_url='login')
def coding_test_result(request, submission_id):
    """Display score, AI insights, and code review."""
    submission = get_object_or_404(CodingSubmission, id=submission_id, user=request.user)
    return render(request, 'preparation_ab/coding_test_result.html', {'submission': submission})


@login_required(login_url='login')
def coding_test_history(request):
    """Lists past coding submissions."""
    submissions = CodingSubmission.objects.filter(user=request.user).order_by('-submitted_at')
    
    # Calculate aggregate stats
    total = submissions.count()
    avg_score = 0
    if total > 0:
        avg_score = round(sum(s.score for s in submissions) / total)
    
    # Language breakdown
    lang_stats = {}
    for s in submissions:
        if s.language not in lang_stats:
            lang_stats[s.language] = {'count': 0, 'total_score': 0}
        lang_stats[s.language]['count'] += 1
        lang_stats[s.language]['total_score'] += s.score
    
    for lang in lang_stats:
        lang_stats[lang]['avg_score'] = round(lang_stats[lang]['total_score'] / lang_stats[lang]['count'])
    
    return render(request, 'preparation_ab/coding_test_history.html', {
        'submissions': submissions,
        'total_submissions': total,
        'avg_score': avg_score,
        'lang_stats': lang_stats,
    })


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# AI CHATBOT ASSISTANT
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@csrf_exempt
def chatbot_api_view(request):
    """
    Handle project-related queries using OpenAI with session-based memory.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Only POST allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '').strip()
        
        if not user_msg:
            return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)

        # Retrieve history from session
        history = request.session.get('chat_history', [])
        
        # System Prompt with Project Context
        system_prompt = {
            "role": "system",
            "content": (
                "You are the PlacementHub AI Assistant. Your goal is to help users understand this platform. "
                "The platform includes: \n"
                "1. Aptitude Assessments: Timed tests (1 min per Q) for Logical, Verbal, and Quantitative reasoning. AI generates fresh questions every time.\n"
                "2. AI Resume Analyzer: Analyzes resumes (PDF/DOCX) for ATS scores, missing keywords, and role matches.\n"
                "3. Coding Arena: A built-in IDE for 8+ languages (Python, Java, etc.) with company-specific challenges and AI code review.\n"
                "4. Mock Interviews: AI-proctored technical/HR rounds with video recording and performance analysis.\n"
                "5. Career Recommendations: Personalized suggestions based on test scores and profile skills.\n\n"
                "Keep responses helpful, concise, and focused on the project functionality. "
                "Mention the benefits of attending assessments: they help track speed, accuracy, and readiness for real company tests."
            )
        }

        # Build prompt with history
        prompt = f"System: {system_prompt['content']}\n\n"
        for h in history[-10:]:
            prompt += f"{h['role']}: {h['content']}\n"
        prompt += f"User: {user_msg}\nAssistant:"

        # Get Gemini Response
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL_FLASH,
            contents=prompt
        )
        ai_msg = response.text.strip()

        # Update history in session
        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": ai_msg})
        request.session['chat_history'] = history
        request.session.modified = True

        return JsonResponse({'status': 'success', 'reply': ai_msg})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ADVANCED PROCTORING (OpenCV + YOLOv8)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@csrf_exempt
@login_required(login_url='login')
def proctor_frame(request):
    """
    Receives a base64 frame, runs YOLOv8 detection, and returns security status.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)
    
    try:
        data = json.loads(request.body)
        image_data = data.get('image', '')
        if not image_data:
            return JsonResponse({'status': 'ok', 'detections': []})

        # Decode base64 image
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        img_bytes = base64.b64decode(imgstr)
        
        # Convert to OpenCV format
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if yolo_model is None:
            return JsonResponse({'status': 'warning', 'message': 'AI Proctoring Offline', 'detections': []})

        # Run YOLOv8 detection
        results = yolo_model(img, verbose=False)
        
        detections = []
        violations = []
        person_count = 0
        
        for r in results:
            for c in r.boxes.cls:
                label = yolo_model.names[int(c)]
                detections.append(label)
                
                if label == 'person':
                    person_count += 1
                if label in ['cell phone', 'laptop', 'book', 'tablet']:
                    violations.append(f"Unauthorized object: {label}")

        if person_count == 0:
            violations.append("No person detected")
        elif person_count > 1:
            violations.append("PROXY ALERT: Multiple people detected!")

        return JsonResponse({
            'status': 'success',
            'detections': detections,
            'violations': violations,
            'secure': len(violations) == 0
        })

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required(login_url='login')
def text_to_speech_api(request):
    """
    Server-side TTS using gTTS (returns audio URL or stream).
    Note: pyttsx3 is local-only; gTTS is better for web.
    """
    text = request.GET.get('text', 'Hello')
    try:
        tts = gTTS(text=text, lang='en')
        # In a real app, you'd save to media or return bytes
        # For simplicity, we'll return a data URI for the browser to play
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_base64 = base64.b64encode(fp.read()).decode('utf-8')
        return JsonResponse({
            'status': 'success',
            'audio_uri': f"data:audio/mp3;base64,{audio_base64}"
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required(login_url='login')
def generate_ai_coding_problem(request):
    """
    Generate a new coding problem for a specific company using OpenAI.
    """
    company = request.GET.get('company', 'TCS')
    difficulty = request.GET.get('difficulty', 'Basic')

    try:
        prompt = f"""
        Generate a professional coding interview problem for the company: "{company}".
        Difficulty level: {difficulty}.
        
        The problem should be unique and not already in common lists.
        Respond ONLY with a valid JSON object containing:
        {{
            "title": "Problem Title",
            "description": "Detailed description with input/output examples",
            "difficulty": "{difficulty}",
            "sample_input": "string",
            "sample_output": "string",
            "test_cases": [
                {{"input": "string", "expected_output": "string"}},
                {{"input": "string", "expected_output": "string"}}
            ],
            "time_limit_minutes": 30
        }}
        """

        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL_PRO,
            contents=prompt,
            config={'response_mime_type': 'application/json'}
        )

        data = json.loads(response.text)
        
        # Save to DB
        problem = CodingProblem.objects.create(
            title=data['title'],
            description=data['description'],
            difficulty=data['difficulty'],
            company_tag=company,
            sample_input=data['sample_input'],
            sample_output=data['sample_output'],
            test_cases=data['test_cases'],
            time_limit_minutes=data.get('time_limit_minutes', 30)
        )
        messages.success(request, f"New {difficulty} problem for {company} has been generated by AI!")
        return redirect('coding_test_list')

    except Exception as e:
        messages.error(request, f"AI Generation failed: {str(e)}")
        return redirect('coding_test_list')


@login_required(login_url='login')
def delete_coding_submission(request, submission_id):
    """Delete a coding submission record."""
    print(f"DEBUG: Delete coding submission called for {submission_id}, method: {request.method}")
    if request.method == 'POST':
        try:
            submission = get_object_or_404(CodingSubmission, id=submission_id, user=request.user)
            submission.delete()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Coding submission deleted.'})
            messages.success(request, 'Coding submission deleted successfully.')
        except Exception as e:
            print(f"DELETE CODING ERROR: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            messages.error(request, f'Error deleting submission: {str(e)}')
    return redirect('coding_test_history')


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# MANUAL CRUD VIEWS
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@login_required(login_url='login')
def create_mock_interview(request):
    """Manually add an interview session record."""
    if request.method == 'POST':
        form = MockInterviewUpdateForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            messages.success(request, 'Manual interview record added.')
            return redirect('interview_history')
    else:
        form = MockInterviewUpdateForm(initial={'title': f"Manual {request.user.username} Session"})
    return render(request, 'preparation_ab/mock_interview_edit.html', {'form': form, 'title': 'Add Manual Interview'})


@login_required(login_url='login')
def update_mock_interview(request, session_id):
    """Update an existing mock interview session."""
    session = get_object_or_404(MockInterviewSession, id=session_id, user=request.user)
    if request.method == 'POST':
        form = MockInterviewUpdateForm(request.POST, instance=session)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interview record updated.')
            return redirect('interview_history')
    else:
        form = MockInterviewUpdateForm(instance=session)
    return render(request, 'preparation_ab/mock_interview_edit.html', {'form': form, 'title': 'Edit Interview Session'})


@login_required(login_url='login')
def create_coding_submission(request):
    """Manually add a coding submission record."""
    if request.method == 'POST':
        form = CodingSubmissionUpdateForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            # For manual entry, we might need a default problem or handle it differently
            # For now, let's just pick the first problem or allow choosing one
            submission.problem = CodingProblem.objects.first() 
            submission.save()
            messages.success(request, 'Manual coding submission added.')
            return redirect('coding_test_history')
    else:
        form = CodingSubmissionUpdateForm(initial={'title': f"Manual Solution"})
    return render(request, 'preparation_ab/coding_test_edit.html', {'form': form, 'title': 'Add Manual Submission'})


@login_required(login_url='login')
def update_coding_submission(request, submission_id):
    """Update an existing coding submission."""
    submission = get_object_or_404(CodingSubmission, id=submission_id, user=request.user)
    if request.method == 'POST':
        form = CodingSubmissionUpdateForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coding submission updated.')
            return redirect('coding_test_history')
    else:
        form = CodingSubmissionUpdateForm(instance=submission)
    return render(request, 'preparation_ab/coding_test_edit.html', {'form': form, 'title': 'Edit Coding Submission'})

