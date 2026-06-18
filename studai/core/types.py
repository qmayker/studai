from pydantic import BaseModel


class Answer(BaseModel):
    letter: str
    text: str


def answers_serializer(answers: list[Answer]) -> list[dict]:
    serialized_data = []
    for answer in answers:
        serialized_data.append(answer.model_dump())
    return serialized_data


class Question(BaseModel):
    question: str
    answers: list[Answer]
    correct_answer_letter: str


class Questions(BaseModel):
    questions: list[Question]
