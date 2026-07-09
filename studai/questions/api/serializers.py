from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db.models import QuerySet
from chat.models import Chat
from quizess.models import TestAtempt
from .fields import RelatedIdField


class AnswerSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=1)
    chat = RelatedIdField(queryset=Chat.objects.none())
    attempt = serializers.PrimaryKeyRelatedField(queryset=TestAtempt.objects.none())

    def __init__(self, *args, chat_qs: QuerySet, attempt_qs: QuerySet, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["chat"].queryset = chat_qs
        self.fields["attempt"].queryset = attempt_qs

    def validate(self, data: dict) -> dict:
        chat: Chat = data["chat"]
        attempt: TestAtempt = data["attempt"]
        if attempt.chat_id != chat.id:
            raise ValidationError()
        return data
