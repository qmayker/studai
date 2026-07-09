from django.db.models import QuerySet, F
from django.urls import reverse
from quizess.models import TestResult, QuestionAttempt
from .answer import AnswerServices


class TestResultServices:
    def __init__(self, result: TestResult):
        self.result = result
        self.answer_service = AnswerServices(result=self.result)

    @staticmethod
    def create(attempt_id: int, user):
        result = TestResult.objects.create(attempt_id=attempt_id, user=user)
        return TestResultServices(result=result)

    @staticmethod
    def get_by_id(result_id: int, user):
        result = TestResult.objects.get(id=result_id, user=user)
        return TestResultServices(result=result)

    @staticmethod
    def get_by_attempt_id(attempt_related_id: int, user):
        result = TestResult.objects.get(
            attempt__related_id=attempt_related_id, user=user
        )
        return TestResultServices(result=result)

    def save_answers(self, questions: QuerySet[QuestionAttempt]):
        self.answer_service.save_answers(questions)

    @staticmethod
    def exists(attempt_related_id: int, user) -> bool:
        return TestResult.objects.filter(
            attempt__related_id=attempt_related_id, user=user
        ).exists()

    def get_answers(self):
        return self.result.answers.all().annotate(
            question_text=F("question__question_text"),
            correct_answer_letter=F("question__correct_answer_letter"),
        )

    @property
    def result_url(self) -> str:
        return reverse("quizess:detail", args=[self.result.id])
