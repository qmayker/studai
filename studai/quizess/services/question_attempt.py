from questions.models import Question
from quizess.models import QuestionAttempt
from .test_attempt import TestAtemptServices


class QuestionAttemptServices:
    def __init__(self, attempt: TestAtemptServices):
        self.attempt = attempt

    def create_question(self, question: Question) -> QuestionAttempt:
        return QuestionAttempt.objects.create(
            attempt=self.attempt,
            question_text=question.question_text,
            answer=None,
            options=question.options,
            correct_answer_letter=question.correct_answer_letter,
        )

    def set_answer(self, id: int, answer: str):
        return QuestionAttempt.objects.filter(id=id, attempt=self.attempt).update(
            answer=answer
        )
