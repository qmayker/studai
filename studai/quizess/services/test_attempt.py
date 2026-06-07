from django.db.models import QuerySet
from logging import Logger
from chat.models import Chat
from quizess.models import TestAtempt, QuestionAttempt


class TestAtemptServices:
    def __init__(self, attempt: TestAtempt, logger: Logger):
        self.attempt = attempt
        self.logger = logger

    @staticmethod
    def create(chat: Chat, user, logger: Logger):
        attempt = TestAtempt.objects.create(chat=chat, user=user)
        return TestAtemptServices(attempt=attempt, logger=logger)

    @staticmethod
    def get(chat: Chat, user, id: int, logger: Logger) -> TestAtempt:
        attempt = TestAtempt.objects.get(chat=chat, user=user, id=id)
        return TestAtemptServices(attempt=attempt, logger=logger)

    def get_result(self, attempts: set[int]) -> QuerySet[QuestionAttempt]:
        return QuestionAttempt.objects.correct_annotated(attempts)
