import asyncio
from collections.abc import Generator
from google import genai
from google.genai import types
from logging import Logger
from decouple import config
from core.types import Questions
from .socket import send_callback


FAKE_RESPONSE = {
    "questions": [
        {
            "question": "What is the primary purpose of Django's ORM?",
            "answers": [
                {"letter": "A", "text": "To manage HTTP requests"},
                {
                    "letter": "B",
                    "text": "To interact with databases using Python objects",
                },
                {"letter": "C", "text": "To create HTML templates"},
                {"letter": "D", "text": "To handle WebSocket connections"},
            ],
            "correct_answer_letter": "B",
        },
        {
            "question": "Which HTTP method is typically used to create a new resource in a REST API?",
            "answers": [
                {"letter": "A", "text": "GET"},
                {"letter": "B", "text": "DELETE"},
                {"letter": "C", "text": "POST"},
                {"letter": "D", "text": "PUT"},
            ],
            "correct_answer_letter": "C",
        },
        {
            "question": "What does Redis primarily store?",
            "answers": [
                {"letter": "A", "text": "Files on disk"},
                {"letter": "B", "text": "Relational tables"},
                {"letter": "C", "text": "In-memory key-value data"},
                {"letter": "D", "text": "Compiled Python bytecode"},
            ],
            "correct_answer_letter": "C",
        },
    ]
}


class GeminiConfig:
    INSTRUCTION = """
    You are a helpful assistant for students. You generate questions based on the provided text.
    Do not use information from outside of the provided text. Generate 5 questions with 4 answer options for each question.
    The answer options should be labeled with letters A, B, C, D. Provide the correct answer letter for each question. 
    """

    @staticmethod
    def api_key():
        return config("GOOGLE_API_KEY")

    @staticmethod
    def tools() -> list[types.Tool]:
        return [types.Tool(google_search=types.GoogleSearch())]

    @staticmethod
    def response_format():
        return Questions.model_json_schema()

    @classmethod
    def get_config(cls):
        return types.GenerateContentConfig(
            system_instruction=cls.INSTRUCTION,
            tools=cls.tools(),
            response_schema=cls.response_format(),
        )


class GeminiAgent:
    CHUNKS_SIZE = 1000

    def __init__(self, config: types.GenerateContentConfig, logger: Logger):
        self.config = config
        self.logger = logger
        self.client = self.get_client()
        if logger:
            self.logger.debug(f"Initialized GeminiAgent with config: {self.config}")

    @staticmethod
    def get_client():
        return genai.Client(api_key=GeminiConfig.api_key())

    @staticmethod
    def divide_into_chunks(text: str):
        for i in range(0, len(text), GeminiAgent.CHUNKS_SIZE):
            yield text[i : i + GeminiAgent.CHUNKS_SIZE]

    def generate_tasks(self, chunks: Generator[str, None, None], chat_id: int):
        questions = asyncio.run(self._generate_tasks(chunks=chunks))
        self.save_questions(questions=questions, chat_id=chat_id)

        send_callback.delay([], chat_id)

    async def _generate_tasks(
        self, chunks: Generator[str, None, None]
    ) -> list[Questions]:
        async with asyncio.TaskGroup() as tg:
            tasks: list[asyncio.Task] = []
            for chunk in chunks:
                tasks.append(
                    tg.create_task(asyncio.to_thread(self._generate_question, chunk))
                )
        questions = [task.result() for task in tasks]
        return questions

    def _generate_question(self, text: str) -> Questions:
        # response = self.client.models.generate_content(
        #     contents=text, model="gemini-3.5-flash"
        # )
        # text_response = response.text
        text_response = FAKE_RESPONSE  # temporary
        return Questions.model_validate(text_response)

    @staticmethod
    def save_questions(questions: list, chat_id: int):
        # TODO - test, remove socket task
        from questions.models import Question
        question_objects = []
        for question in questions:
            answers = question.model_dump()["answers"]
            question_objects.append(
                Question(
                    chat_id=chat_id,
                    question_text=question.question,
                    correct_answer_letter=question.correct_answer_letter,
                    options=answers,
                )
            )
        question_objects.objects.bulk_create(question_objects)
