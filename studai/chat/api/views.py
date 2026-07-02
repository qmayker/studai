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
from chat.services.contents import (
    TextContentServices,
    ImageContentServices,
)
from chat.services.content import ContentServices, ContentValidator
from chat.services.serializer_fields import SocketIdField, TextField, ImageField
from chat.services.serializer_data import SerializerDataService
from chat.types.serializer import SerializerFields
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

    @action(detail=True, methods=["post"])
    def save_content(self, request: Request, pk=None):
        chat = get_object_or_404(self.get_queryset(request.user), pk=pk)

        data_service = SerializerDataService()
        data = data_service.get_serializer_data(
            **self._get_content_fields(request=request)
        )
        validated_data = ContentValidator.validate_contents(data)

        service = ContentServices(
            *self._get_services(data=validated_data, chat=chat, user=request.user),
            socket_id=validated_data.get("socket_id"),
        )
        saved_contents = service.save()
        
        serializer = ContentSerializer(saved_contents, many=True)
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

    def _get_services(self, data: dict, chat: Chat, user):
        return (
            ImageContentServices(
                images=data.get("image"),
                user=user,
                chat=chat,
                socket_id=data.get("socket_id"),
            ),
            TextContentServices(
                text_content=data.get("text").get("text_content"), user=user, chat=chat
            ),
        )

    def _get_content_fields(self, request: Request):
        fields = {
            "image": SerializerFields(
                field=ImageField, data=request.data.getlist("image_content")
            ),
            "text": SerializerFields(
                field=TextField, data=request.data.get("text_content")
            ),
            "socket_id": SerializerFields(
                field=SocketIdField,
                data=request.data.get("socket_id"),
            ),
        }
        return fields
