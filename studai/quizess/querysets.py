from django.db.models import QuerySet, F, Case, When, Value


class QuestionAttemptQueryset(QuerySet):
    def correct_annotated(self, questions: list[int]):
        return self.filter(id__in=questions).annotate(
            correct=Case(
                When(answer=F("correct_answer_letter"), then=Value(True)),
                default=Value(False),
            )
        )
