from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from chat.models import TextItem, Chat, Content


class SaveContentApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        data = request.data
        print(data)
        text_content = data.get("text_content")
        chat_related_id = data.get("chat_related_id")
        chat = Chat.objects.get(related_id=chat_related_id, user=request.user)
        with transaction.atomic():
            text_item = TextItem.objects.create(text_content=text_content) 
            Content.objects.create(chat=chat, content_object=text_item)
        return Response({"status": "ok"})
