from uuid import UUID
from django.db.models import F, QuerySet
from logging import getLogger
from chat.models import Chat
from quizess.models import TestAtempt, QuestionAttempt

logger = getLogger(__name__)


class TestAtemptServices:
    def __init__(self, attempt_id: int):
        self.id = attempt_id

    @staticmethod
    def create(chat: Chat, user) -> TestAtempt:
        attempt = TestAtempt.objects.create(chat=chat, user=user)
        return attempt

    @staticmethod
    def get(chat: Chat, user, id: int) -> TestAtempt:
        attempt = TestAtempt.objects.get(chat=chat, user=user, id=id)
        return attempt

    @staticmethod
    def get_result(attempts: set[int]) -> QuerySet[QuestionAttempt]:
        return QuestionAttempt.objects.filter_by_ids(attempts)

    def next_order(self):
        TestAtempt.objects.filter(id=self.id).update(order=F("order") + 1)
