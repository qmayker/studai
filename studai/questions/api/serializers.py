from rest_framework import serializers
from django.db.models import QuerySet
from chat.models import Chat
from .fields import RelatedIdField


class AnswerSerializer(serializers.Serializer):
    answer = serializers.CharField(max_length=1)
    chat = RelatedIdField(queryset=Chat.objects.none())

    def __init__(self, *args, qs: QuerySet, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["chat"].queryset = qs
