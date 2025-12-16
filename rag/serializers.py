import os
from rest_framework import serializers
from .models import UploadedDocument, ChatHistory


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDocument
        fields = ['file']

    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']

        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                "Only PDF, DOC, DOCX, and TXT files are allowed."
            )

        max_size = 10 * 1024 * 1024  # 10 MB
        if value.size > max_size:
            raise serializers.ValidationError(
                "File size cannot exceed 10 MB."
            )

        return value


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedDocument
        fields = [
            'id',
            'file',
            'file_type',
            'uploaded_at',
            'processed',
            'chunk_count',
        ]
        read_only_fields = fields


class ChatRequestSerializer(serializers.Serializer):
    """
    Serializer for /chat input
    """
    message = serializers.CharField(max_length=1000)


class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = [
            'id',
            'user_message',
            'ai_response',
            'created_at',
        ]
