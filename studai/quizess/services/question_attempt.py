from django.db.models import QuerySet
from django.http import Http404
from questions.models import Question
from quizess.models import QuestionAttempt


class QuestionAttemptServices:
    def __init__(self, attemp_id: int):
        self.attempt_id = attemp_id

    def _create_kwargs(self, question: Question, order: int) -> dict:
        return {
            "attempt_id": self.attempt_id,
            "question_text": question.question_text,
            "answer": None,
            "options": question.options,
            "correct_answer_letter": question.correct_answer_letter,
            "order": order,
        }

    def create_question(self, question: Question, order: int = 0) -> QuestionAttempt:
        return QuestionAttempt.objects.create(
            **self._create_kwargs(question=question, order=order)
        )

    def bulk_create_questions(self, questions: list[Question]) -> QuestionAttempt:
        question_attempts = []
        for order, question in enumerate(questions):
            question_attempts.append(
                QuestionAttempt(**self._create_kwargs(question=question, order=order))
            )
        QuestionAttempt.objects.bulk_create(objs=question_attempts)

    def get_queryset(self):
        queryset = QuestionAttempt.objects.filter(attempt_id=self.attempt_id)
        return queryset

    @staticmethod
    def set_answer(qs: QuerySet[QuestionAttempt], order: int, answer: str):
        return qs.filter(order=order).update(answer=answer)

    @staticmethod
    def get_question(qs: QuerySet[QuestionAttempt], id: int) -> QuestionAttempt:
        return qs.get(id=id)

    def get_by_order(self, order: int) -> QuestionAttempt:
        return self.get_queryset().get(order=order)

    def get_or_create_question_attempt(
        self, question: Question | None, question_attempt_id: int | None
    ) -> QuestionAttempt:
        if question_attempt_id:
            qs = self.get_queryset()
            question_attempt = self.get_question(qs=qs, id=question_attempt_id)
        elif question:
            question_attempt = self.create_question(question=question)
        else:
            raise Http404()
        return question_attempt

    def get_order_queryset(self, order: int) -> QuerySet:
        return QuestionAttempt.objects.filter(
            attempt_id=self.attempt_id, order__gt=order
        )

    @staticmethod
    def is_last(qs: QuerySet):
        if not qs.exists():
            return True
        return False

    def get_next_question(self, order: int) -> QuestionAttempt | None:
        qs = self.get_order_queryset(order=order)
        if self.is_last(qs=qs):
            return None
        return qs.first()
