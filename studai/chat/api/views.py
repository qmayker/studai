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
from chat.services.serializer_data import SerializerDataServices
from chat.types.serializer import SerializerFields
from chat.tasks.questions import generate_questions
from websocket.models import UserSocket
from .serializers import ContentSerializer, SocketSerializer


logger = logging.getLogger(__name__)


class ChatViewSet(ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self, user):
        queryset = Chat.objects.filter(user=user)
        return queryset

    def get_chat(self, pk: str | int):
        qs = self.get_queryset(self.request.user)
        return get_object_or_404(queryset=qs, pk=pk)

    @action(detail=True, methods=["post"])
    def save_content(self, request: Request, pk=None):
        chat = self.get_chat()

        data = SerializerDataServices.get_serializer_data(
            **self._get_content_fields(request=request)
        )
        validated_data = ContentValidator.validate_contents(
            data,
            context={"socket_queryset": UserSocket.objects.filter(user=request.user)},
        )
        socket: UserSocket = validated_data.get("socket").get("socket")

        service = ContentServices(
            *self._get_services(data=validated_data, chat=chat, user=request.user),
            socket_id=socket.socket_id,
        )
        saved_contents = service.save()

        serializer = ContentSerializer(saved_contents, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def generate_questions(self, request: Request, pk=None):
        chat = self.get_chat(pk=pk)
        data = SocketIdField.get_data(data=request.POST.get("socket_id"))
        serializer = SocketSerializer(
            data=data,
            context={"socket_queryset": UserSocket.objects.filter(user=request.user)},
        )
        serializer.is_valid()
        serializer.is_valid(raise_exception=True)
        socket: UserSocket = serializer.validated_data["socket"]

        generate_questions.delay(pk, request.user.id, socket.socket_id, chat.related_id)
        return Response({"status": "ok"})

    @action(detail=True, methods=["get"])
    def get_contents(self, request: Request, pk=None):
        chat = self.get_chat(pk=pk)
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
            "socket": SerializerFields(
                field=SocketIdField,
                data=request.data.get("socket_id"),
            ),
        }
        return fields
