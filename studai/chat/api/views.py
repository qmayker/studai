import logging
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from chat.models import Chat
from chat.services.text_content import TextContentServices
from studai.celery import generate_questions
from .serializers import ContentSerializer

# TODO - business logic to services

logger = logging.getLogger(__name__)


class ChatViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, user):
        queryset = Chat.objects.filter(user=user)
        return queryset

    def check_permission(self, pk: str | int, user):
        qs = self.get_queryset(user).filter(pk=pk)
        if not qs.exists():
            raise PermissionDenied()

    @action(detail=True, methods=["post"])
    def save_content(self, request: Request, pk=None):
        text_content = TextContentServices.get_text_content(request.data)
        chat = get_object_or_404(self.get_queryset(request.user), pk=pk)
        TextContentServices.save_text_content(chat=chat, text_content=text_content)
        return Response({"status": "created"})

    @action(detail=True, methods=["get"])
    def generate_questions(self, request: Request, pk=None):
        self.check_permission(pk, request.user)
        generate_questions.delay(pk, request.user.id)
        return Response({"status": "ok"})

    @action(detail=True, methods=["get"])
    def get_contents(self, request: Request, pk=None):
        chat = get_object_or_404(self.get_queryset(request.user), pk=pk)
        serializer = ContentSerializer(chat.contents.all(), many=True)
        return Response(serializer.data)
