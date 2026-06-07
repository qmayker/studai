from django.db.models import QuerySet
from quizess.models import TestResult, TestAtempt, QuestionAttempt
from .answer import AnswerServices


class TestResultServices:
    def __init__(self, result: TestResult):
        self.result = result
        self.answer_service = AnswerServices(result=self.result)

    @staticmethod
    def create(attempt: TestAtempt, user):
        result = TestResult.objects.create(attempt=attempt, user=user)
        return TestResultServices(result=result)
    
    @staticmethod
    def get_by_attempt_id(attempt_id:int, user):
        result = TestResult.objects.get(attempt_id=attempt_id, user=user)
        return TestResultServices(result=result)

    def save_answers(self, questions: QuerySet[QuestionAttempt]):
        self.answer_service.save_answers(questions)
