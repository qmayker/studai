from django.db.models import QuerySet


class QuestionAttemptQueryset(QuerySet):
    def filter_by_ids(self, question_ids: list[int]):
        return self.filter(id__in=question_ids)
