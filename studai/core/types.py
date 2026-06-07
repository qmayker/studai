from pydantic import BaseModel


class Answer(BaseModel):
    letter: str
    text: str


class Question(BaseModel):
    question: str
    answers: list[Answer]
    correct_answer_letter: str


class Questions(BaseModel):
    questions: list[Question]
