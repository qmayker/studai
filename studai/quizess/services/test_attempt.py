from django.db.models import QuerySet
from logging import Logger
from chat.models import Chat
from quizess.models import TestAtempt
from quizess.models import QuestionAttempt


class TestAtemptServices:
    def __init__(self, chat: Chat, user):
        self.chat = chat
        self.user = user

    def create(self) -> TestAtempt:
        return TestAtempt.objects.create(chat=self.chat, user=self.user)

    def get(self, id: int) -> TestAtempt:
        return TestAtempt.objects.get(chat=self.chat, user=self.user, id=id)

    @staticmethod
    def end(attempts: set[int]) -> QuerySet[QuestionAttempt]:
        #TODO
        answers: QuerySet[QuestionAttempt] = QuestionAttempt.objects.correct_annotated(
            attempts
        )
        for answer in answers:
            ...
        return answers
