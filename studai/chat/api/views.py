from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from chat.models import TextItem, Chat, Content
from studai.celery import generate_questions


class SaveContentApi(APIView):
    permission_classes = [IsAuthenticated]

    # TODO fix id problem
    def post(self, request, format=None):
        data = request.data
        print(data)
        text_content = data.get("text_content")
        chat_id = data.get("chat_id")
        chat = Chat.objects.get(pk=chat_id, user=request.user)
        with transaction.atomic():
            text_item = TextItem.objects.create(text_content=text_content)
            Content.objects.create(chat=chat, content_object=text_item)
        return Response({"status": "ok"})


class GenerateQuestionsApi(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        data = request.data
        chat_related_id = data.get("chat_related_id")
        generate_questions.delay(chat_related_id)
        return Response({"status": "ok"})
