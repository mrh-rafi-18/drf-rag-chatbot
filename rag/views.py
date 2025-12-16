import logging

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .models import UploadedDocument, ChatHistory
from .serializers import (
    DocumentUploadSerializer,
    ChatRequestSerializer,
    ChatHistorySerializer,
)
from .rag_pipeline import RAGPipeline  # your RAG pipeline class


logger = logging.getLogger(__name__)


class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Upload document",
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "format": "binary"
                    }
                },
                "required": ["file"]
            }
        },
        responses={201: {"message": "File uploaded successfully"}}
    )
    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file = serializer.validated_data["file"]
        ext = file.name.split(".")[-1].lower()

        document = serializer.save(
            user=request.user,
            file_type=ext
        )

        try:
            rag = RAGPipeline(user_id=request.user.id)
            chunk_count = rag.process_document(
                file_path=document.file.path,
                doc_id=document.id
            )

            if chunk_count > 0:
                document.processed = True
                document.chunk_count = chunk_count
                document.save()

            return Response(
                {"message": "File uploaded successfully"},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            document.delete()
            return Response(
                {"error": "Document processing failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Chat with RAG",
        request=ChatRequestSerializer,
        responses={200: dict}
    )
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data["message"]

        try:
            rag = RAGPipeline(user_id=request.user.id)
            result = rag.query(user_message)

            ai_response = result.get("answer", "")

            ChatHistory.objects.create(
                user=request.user,
                user_message=user_message,
                ai_response=ai_response
            )

            return Response(
                {
                    "message": user_message,
                    "answer": ai_response,
                    "sources": result.get("sources", [])
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Chat error: {e}")
            return Response(
                {"error": "Failed to process chat"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get chat history",
        responses={200: ChatHistorySerializer(many=True)}
    )
    def get(self, request):
        history = ChatHistory.objects.filter(
            user=request.user
        ).order_by("-created_at")

        serializer = ChatHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
