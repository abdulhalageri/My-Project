from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Category, Question, AssessmentAttempt, 
    CodingProblem, CodingSubmission, MockInterviewSession, InterviewQuestion
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'year_of_passing')
    list_filter = ('role', 'department', 'year_of_passing')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Placement Info', {
            'fields': ('role', 'phone', 'department', 'year_of_passing', 'cgpa', 'profile_picture', 'bio', 'skills', 'linkedin_url', 'github_url')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Placement Info', {
            'fields': ('role', 'phone', 'department', 'year_of_passing', 'cgpa')
        }),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'time_per_question')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'is_ai_generated')
    list_filter = ('category', 'is_ai_generated')


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'score', 'total_questions', 'completed_at')
    list_filter = ('category', 'completed_at')


@admin.register(CodingProblem)
class CodingProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_tag', 'difficulty', 'time_limit_minutes')
    list_filter = ('company_tag', 'difficulty')
    search_fields = ('title', 'description')


@admin.register(CodingSubmission)
class CodingSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'problem', 'language', 'score', 'submitted_at')
    list_filter = ('language', 'submitted_at')


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'round_type')
    list_filter = ('round_type',)


@admin.register(MockInterviewSession)
class MockInterviewSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'round_type', 'status', 'score', 'created_at')
    list_filter = ('round_type', 'status', 'created_at')