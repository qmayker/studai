from django.db.transaction import atomic
from questions.models import Question
from questions.services.question import QuestionServices
from quizess.models import QuestionAttempt
from quizess.services.test_result import TestResultServices
from quizess.services.question_attempt import QuestionAttemptServices
from quizess.types.quizz import GetResult


class QuizzServices:
    def __init__(self, qa_service: QuestionAttemptServices):
        self.question_attempt_service = qa_service

    def get_question_attempt(self, order: int) -> QuestionAttempt | None:
        try:
            return self.question_attempt_service.get_by_order(order=order)
        except QuestionAttempt.DoesNotExist:
            return self.question_attempt_service.get_next_question(order=order)

    def start(self, qs):
        questions: list[Question] = list(qs)
        QuestionServices.shuffle_questions(questions=questions)
        self.question_attempt_service.bulk_create_questions(questions=questions)

    @atomic
    def save_quizz_result(self, user) -> TestResultServices:
        result = TestResultServices.create(
            attempt_id=self.question_attempt_service.attempt_id, user=user
        )
        result.save_answers(self.question_attempt_service.get_queryset())
        return result

    def get(self, user, order_id: int) -> GetResult:
        question_attempt = self.get_question_attempt(order=order_id)
        if not question_attempt:
            res = self.save_quizz_result(user=user)
            return GetResult(end=True, result=res.result_url)
        service = question_attempt.service
        return GetResult(end=False, result=service)
