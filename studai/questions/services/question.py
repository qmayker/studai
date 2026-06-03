import random
from django.db.models import QuerySet


class QuestionServices:
    def __init__(
        self,
        options: dict,
        question_name: str,
        correct_answer_letter: str,
    ):
        self.question_name = question_name
        self.correct_answer_letter = correct_answer_letter
        self.options = options

    @property
    def option_letters(self) -> list[str]:
        letters = []
        for option in self.options:
            letters.append(option["letter"])
        return letters

    @property
    def get_answer_text(self, letter: str) -> str | None:
        return self.options.get(letter)

    def is_correct(self, answer_letter: str) -> bool:
        return answer_letter.upper() == self.correct_answer_letter.upper()

    def generate_random_questions_id(chat_related_id: int, qs: QuerySet):
        question_ids = list(qs.values_list("id", flat=True))
        random.shuffle(question_ids)
        return question_ids

    def __str__(self):
        return self.question_name
