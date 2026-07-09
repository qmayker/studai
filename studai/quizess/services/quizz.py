from django.db.transaction import atomic, on_commit
from questions.models import Question
from questions.services.question import QuestionServices
from questions.services.sessions import QuestionSessionServices
from quizess.services.test_attempt import TestAtemptServices
from quizess.services.test_result import TestResultServices
from quizess.services.question_attempt import QuestionAttemptServices
from quizess.types.quizz import GetResult


class QuizzServices:
    def __init__(self, session: QuestionSessionServices):
        self.session = session

    def get_question(self, question_id: int, qs) -> Question | None:
        try:
            question = QuestionServices.get_question(qs=qs, pk=question_id)
        except Question.DoesNotExist:
            if self.session.last_id:
                return None
            self.session.delete_id(question_id=question_id)
            return self.get_question(qs=qs, question_id=self.session.current_id)
        return question

    def start_session(self, qs):
        ids = QuestionServices.get_random_question_ids(qs=qs)
        self.session.start(questions=ids)

    def check_session(self, qs):
        if not self.session.active:
            self.start_session(qs=qs)

    @atomic
    def save_quizz_result(self, user) -> TestResultServices:
        result = TestResultServices.create(
            attempt_id=self.session.attempt_id, user=user
        )
        result.save_answers(TestAtemptServices.get_result(self.session.attempt_ids))
        on_commit(self.session.clear)
        return result

    def get(
        self, qs, question_attempt_service: QuestionAttemptServices, user
    ) -> GetResult:
        question_id = self.session.current_id
        question_attempt_id = self.session.get_question_attempt_id(
            question_id=question_id
        )
        if not question_attempt_id:
            question = self.get_question(question_id=question_id, qs=qs)
            if not question:
                res = self.save_quizz_result(user=user)
                return GetResult(end=True, result=res.result_url)
        else:
            question = None
        question_attempt = question_attempt_service.get_or_create_question_attempt(
            question=question, question_attempt_id=question_attempt_id
        )
        self.session.add_question_attempt(question_attempt_id=question_attempt.id)
        service = question_attempt.service
        return GetResult(end=False, result=service)
