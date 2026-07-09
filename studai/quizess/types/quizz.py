from typing import NamedTuple
from questions.services.question import QuestionServices


class GetResult(NamedTuple):
    end: bool
    result: str | QuestionServices
