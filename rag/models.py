from django.conf import settings
from django.db import models
import os


User = settings.AUTH_USER_MODEL


class UploadedDocument(models.Model):
    FILE_TYPES = (
        ('pdf', 'PDF'),
        ('doc', 'DOC'),
        ('docx', 'DOCX'),
        ('txt', 'TXT'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_documents'
    )
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # RAG-related metadata
    processed = models.BooleanField(default=False)
    chunk_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.file.name} uploaded by {self.user.username}"

    def delete(self, *args, **kwargs):
        # Ensure file is removed from disk
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-uploaded_at']


class ChatHistory(models.Model):
    """
    Stores chat messages between user and AI.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_history'
    )
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.user_message[:40]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Chat Histories"
