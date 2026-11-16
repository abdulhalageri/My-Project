from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, MockInterviewSession, CodingSubmission, CodingProblem
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.core.validators import RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
import re


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email Address'
    }))
    
    first_name = forms.CharField(
        max_length=100, 
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'First name should only contain alphabets.')],
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'First Name'
        })
    )
    
    last_name = forms.CharField(
        max_length=100, 
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Last name should only contain alphabets.')],
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Last Name'
        })
    )
    
    phone = forms.CharField(
        max_length=15, 
        required=False, 
        validators=[RegexValidator(r'^\d+$', 'Phone number should only contain numeric digits.')],
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Phone Number'
        })
    )
    
    department = forms.ChoiceField(
        choices=CustomUser.DEPARTMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-input',
        })
    )
    
    year_of_passing = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-input',
        'placeholder': 'Year of Passing'
    }))

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone',
                  'department', 'year_of_passing']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Username'})
        self.fields['username'].validators.append(RegexValidator(r'^[a-zA-Z0-9]+$', 'Username should be alphanumeric.'))
        self.fields['username'].validators.append(MinLengthValidator(6, 'Username must be at least 6 characters long.'))
        
        # UserCreationForm (v6.0+) uses password1 and password2
        # We need to style them too
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Password'})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Confirm Password'})

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter.")
            if not re.search(r'[a-z]', password):
                raise ValidationError("Password must contain at least one lowercase letter.")
            if not re.search(r'[0-9]', password):
                raise ValidationError("Password must contain at least one number.")
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError("Password must contain at least one special character.")
        return password


class LoginForm(AuthenticationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password'
    }))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'department',
                  'year_of_passing', 'cgpa', 'bio', 'skills', 'linkedin_url',
                  'github_url', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'department': forms.Select(choices=CustomUser.DEPARTMENT_CHOICES, attrs={'class': 'form-input'}),
            'year_of_passing': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Year of Passing'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'CGPA', 'step': '0.01'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'About You', 'rows': 4}),
            'skills': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Skills (comma-separated)', 'rows': 3}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'LinkedIn URL'}),
            'github_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'GitHub URL'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add validators to profile fields
        self.fields['first_name'].validators.append(RegexValidator(r'^[a-zA-Z\s]+$', 'First name should only contain alphabets.'))
        self.fields['last_name'].validators.append(RegexValidator(r'^[a-zA-Z\s]+$', 'Last name should only contain alphabets.'))
        self.fields['phone'].validators.append(RegexValidator(r'^\d+$', 'Phone number should only contain numeric digits.'))


class AssessmentForm(forms.Form):
    """Dynamically generated form for assessment questions."""
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        for q in questions:
            self.fields[f'question_{q.id}'] = forms.ChoiceField(
                label=q.text,
                choices=[('A', q.option_a), ('B', q.option_b), ('C', q.option_c), ('D', q.option_d)],
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
            )


class MockInterviewUpdateForm(forms.ModelForm):
    class Meta:
        model = MockInterviewSession
        fields = ['title', 'user_notes', 'round_type', 'status', 'score', 'feedback']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Session Title'}),
            'user_notes': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Personal Reflections', 'rows': 4}),
            'round_type': forms.Select(choices=[('HR', 'HR Round'), ('Technical', 'Technical Round')], attrs={'class': 'form-input'}),
            'status': forms.Select(choices=[('Completed', 'Completed'), ('Failed', 'Failed')], attrs={'class': 'form-input'}),
            'score': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 100}),
            'feedback': forms.Textarea(attrs={'class': 'form-input', 'rows': 6}),
        }


class CodingSubmissionUpdateForm(forms.ModelForm):
    class Meta:
        model = CodingSubmission
        fields = ['title', 'user_notes', 'language', 'score', 'ai_feedback']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Submission Title'}),
            'user_notes': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Personal reflections...', 'rows': 4}),
            'language': forms.TextInput(attrs={'class': 'form-input'}),
            'score': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 100}),
            'ai_feedback': forms.Textarea(attrs={'class': 'form-input', 'rows': 6}),
        }