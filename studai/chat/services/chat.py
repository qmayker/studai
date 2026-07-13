from questions.models import Question
from chat.models import Chat


class ChatServices:
    @staticmethod
    def delete_chat_questions(chat_id: int):
        Question.objects.filter(chat_id=chat_id).delete()

    @staticmethod
    def get(chat_id: int, **kwargs):
        return Chat.objects.get(id=chat_id, **kwargs)
