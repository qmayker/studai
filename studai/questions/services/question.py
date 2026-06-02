from logging import Logger


class QuestionServices:
    def __init__(
        self,
        logger: Logger,
        answers: dict,
        question_name: str,
        correct_answer_letter: str,
    ):
        self.name = question_name
        self.logger = logger
        self.correct_answer_letter = correct_answer_letter
        self.answers = answers

    def is_correct(self, answer_letter: str) -> bool:
        return answer_letter.upper() == self.correct_answer_letter.upper()
