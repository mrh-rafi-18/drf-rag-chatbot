from django.urls import path
from .views import (
    DocumentUploadView,
    ChatView,
    ChatHistoryView,
)

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='upload'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('chat-history/', ChatHistoryView.as_view(), name='chat-history'),
]
