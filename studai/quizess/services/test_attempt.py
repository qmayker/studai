from django.db.models import QuerySet
from logging import getLogger
from chat.models import Chat
from quizess.models import TestAtempt, QuestionAttempt

logger = getLogger(__name__)


class TestAtemptServices:
    def __init__(self, attempt: TestAtempt):
        self.attempt = attempt

    @staticmethod
    def create(chat: Chat, user):
        attempt = TestAtempt.objects.create(chat=chat, user=user)
        return TestAtemptServices(attempt=attempt)

    @staticmethod
    def get(chat: Chat, user, id: int):
        attempt = TestAtempt.objects.get(chat=chat, user=user, id=id)
        return TestAtemptServices(attempt=attempt)

    @staticmethod
    def get_result(attempts: set[int]) -> QuerySet[QuestionAttempt]:
        return QuestionAttempt.objects.filter_by_ids(attempts)
