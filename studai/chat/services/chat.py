from questions.models import Question


class ChatServices:
    @staticmethod
    def delete_chat_questions(chat_id: int):
        Question.objects.filter(chat_id=chat_id).delete()
