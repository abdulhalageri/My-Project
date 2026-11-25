
"""
URL configuration for portal_ui project.

The urlpatterns list routes URLs to views.
"""

from preparation_ab import views as preparation_views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # Serve interview recordings with HTTP Range support
    path(
        'media/interview_recordings/<str:filename>',
        preparation_views.serve_interview_recording,
        name='serve_interview_recording'
    ),

    # Application URLs
    path('', include('preparation_ab.urls')),
]


# Serve other media and static files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
