from rest_framework.serializers import ModelSerializer
from rest_framework.fields import SerializerMethodField
from chat.models import Content

class ContentSerializer(ModelSerializer):
    content = SerializerMethodField()
    class Meta:
        model = Content
        fields = ['id', 'content']

    def get_content(self, obj:Content):
        return obj.get_content()
