from collections.abc import Generator
from celery import chord, shared_task
from celery.app.log import get_logger
from google import genai
from google.genai import types
from logging import Logger
from pydantic import BaseModel
from decouple import config
from chat.models import Chat
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


class Answer(BaseModel):
    letter: str
    text: str


class Question(BaseModel):
    question: str
    answers: list[Answer]
    correct_answer_letter: str


class Questions(BaseModel):
    questions: list[Question]


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

    def __init__(
        self, config: types.GenerateContentConfig, logger: Logger | None = None
    ):
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

    def test(self):
        response = self.client.models.generate_content(
            model="gemini-3.5-flash",
            config=self.config,
            contents="How does LLM work? Explain like I am 10 years old.",
        )
        self.logger.info(f"Received response: {response.text}")

    def generate_tasks(self, chunks: Generator[str, None, None], chat_id: int):
        tasks = []
        for chunk in chunks:
            if self.logger:
                self.logger.info(f"Processing chunk: {chunk[:50]}...")
            tasks.append(process_chunk.s(chunk, chat_id=chat_id))
        chord(tasks)(send_callback.s(chat_id=chat_id))

    def _generate_question(self, text: str):
        return FAKE_RESPONSE


@shared_task
def process_chunk(chunk: str, chat_id: int):
    logger = get_logger(__name__)
    agent = GeminiAgent(config=GeminiConfig.get_config(), logger=logger)
    response = agent._generate_question(text=chunk)
    # TODO - save response to db and send to ws
