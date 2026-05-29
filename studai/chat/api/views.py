import logging
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from chat.models import TextItem, Chat, Content
from studai.celery import generate_questions
from .serializers import ContentSerializer

# TODO - business logic to services

logger = logging.getLogger(__name__)


class ChatViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, user):
        queryset = Chat.objects.filter(user=user)
        return queryset

    def is_owned(self, pk: str | int, user) -> bool:
        qs = self.get_queryset(user).filter(pk=pk)
        return qs.exists()

    @action(detail=True, methods=["post"])
    def save_content(self, request: Request, pk=None):
        chat = get_object_or_404(self.get_queryset(request.user), pk=pk)
        text_content = request.data.get("text_content")
        if not text_content:
            return Response(
                {"status": "not created", "message": "text_content can`t be empty"}
            )
        with transaction.atomic():
            text_item = TextItem.objects.create(text_content=text_content)
            Content.objects.create(chat=chat, content_object=text_item)
        return Response({"status": "created"})

    @action(detail=True, methods=["get"])
    def generate_questions(self, request: Request, pk=None):
        if not self.is_owned(pk=pk, user=request.user):
            return Response({"status": "error"})
        generate_questions.delay(pk)
        return Response({"status": "ok"})

    @action(detail=True, methods=["get"])
    def get_contents(self, request: Request, pk=None):
        chat = get_object_or_404(self.get_queryset(request.user), pk=pk)
        serializer = ContentSerializer(chat.contents.all(), many=True)
        return Response(serializer.data)
