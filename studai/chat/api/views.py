import logging
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.viewsets import ViewSet
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from chat.models import Chat
from chat.services.text_content import TextContentServices
from chat.services.image_content import ImageContentServices
from chat.services.content import ContentServices
from studai.celery import generate_questions
from .serializers import ContentSerializer


logger = logging.getLogger(__name__)


class ChatViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self, user):
        queryset = Chat.objects.filter(user=user)
        return queryset

    def check_permission(self, pk: str | int, user):
        qs = self.get_queryset(user).filter(pk=pk)
        if not qs.exists():
            raise PermissionDenied()

    def get_content_service(self, request: Request, chat: Chat):
        text_service = TextContentServices.get_service(data=request.data)
        image_service = ImageContentServices.get_service(
            images=request.FILES.getlist("image_content")
        )
        return ContentServices(
            image_service=image_service,
            text_service=text_service,
            chat=chat,
            user=request.user,
        )

    @action(detail=True, methods=["post"])
    def save_content(self, request: Request, pk=None):
        chat = get_object_or_404(self.get_queryset(request.user), pk=pk)
        service = self.get_content_service(request=request, chat=chat)
        contents = service.save()
        serializer = ContentSerializer(contents, many=True)
        return Response(serializer.data)

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
