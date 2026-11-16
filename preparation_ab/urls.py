from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('resume/', views.resume_upload_view, name='resume_upload'),
    path('resume/delete/<int:resume_id>/', views.delete_resume, name='delete_resume'),

    # Profile CRUD
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    # Assessment Module
    path('assessments/', views.assessment_list_view, name='assessment_list'),
    path('assessments/take/<int:category_id>/', views.take_assessment_view, name='take_assessment'),
    path('assessments/result/<int:attempt_id>/', views.assessment_result_view, name='assessment_result'),

    # Recommendations
    path('recommendations/', views.recommendation_view, name='recommendations'),

    # Mock Interview Module
    path('interviews/', views.mock_interview_list, name='mock_interview_list'),
    path('interviews/session/<str:round_type>/', views.mock_interview_session, name='mock_interview_session'),
    path('mock-interview/process/', views.process_mock_interview, name='process_mock_interview'),
    path('mock-interview/upload-video/', views.upload_interview_video, name='upload_interview_video'),
    path('interview/start/', views.mock_interview_session, name='mock_interview_session'),
    path('interview/proctor/frame/', views.proctor_frame, name='proctor_frame'),
    path('interview/tts/', views.text_to_speech_api, name='tts_api'),
    path('interview/result/<int:session_id>/', views.mock_interview_result, name='mock_interview_result'),
    path('mock-interview/history/', views.interview_history, name='interview_history'),
    path('mock-interview/add/', views.create_mock_interview, name='create_mock_interview'),
    path('mock-interview/update/<int:session_id>/', views.update_mock_interview, name='update_mock_interview'),
    path('mock-interview/delete/<int:session_id>/', views.delete_mock_interview, name='delete_mock_interview'),

    # Coding Test Module
    path('coding/', views.coding_test_list, name='coding_test_list'),
    path('coding/session/<int:problem_id>/', views.coding_test_session, name='coding_test_session'),
    path('coding/submit/', views.submit_coding_test, name='submit_coding_test'),
    path('coding/result/<int:submission_id>/', views.coding_test_result, name='coding_test_result'),
    path('coding/history/', views.coding_test_history, name='coding_test_history'),
    path('coding/add/', views.create_coding_submission, name='create_coding_submission'),
    path('coding/update/<int:submission_id>/', views.update_coding_submission, name='update_coding_submission'),
    path('coding/delete/<int:submission_id>/', views.delete_coding_submission, name='delete_coding_submission'),
    path('coding/generate/', views.generate_ai_coding_problem, name='generate_coding_problem'),
    path('chatbot/', views.chatbot_api_view, name='chatbot_api'),
]
