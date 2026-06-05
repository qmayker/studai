from quizess.models import TestAtempt
from chat.models import Chat


class TestAtemptServices:
    def __init__(self, chat: Chat, user):
        self.chat = chat
        self.user = user

    def create(self) -> TestAtempt:
        return TestAtempt.objects.create(chat=self.chat, user=self.user)

    def get(self, id: int) -> TestAtempt:
        return TestAtempt.objects.get(chat=self.chat, user=self.user, id=id)
