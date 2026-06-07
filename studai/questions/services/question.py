import random
from django.db.models import QuerySet


class QuestionServices:
    def __init__(
        self,
        options: list[dict],
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

    @property
    def choices(self) -> list[tuple[str, str]]:
        choices = []
        for option_info in self.options:
            letter = option_info["letter"]
            text = option_info["text"]
            choices.append((letter, f"{letter}. {text}"))
        return choices

    def is_correct(self, answer_letter: str) -> bool:
        return answer_letter.upper() == self.correct_answer_letter.upper()

    def get_random_question_ids(qs: QuerySet):
        question_ids = list(qs.values_list("id", flat=True))
        random.shuffle(question_ids)
        return question_ids

    @staticmethod
    def get_question(qs: QuerySet, pk: int):
        return qs.get(pk=pk)

    def __str__(self):
        return self.question_name
