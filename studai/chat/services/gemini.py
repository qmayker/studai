from google import genai
from logging import Logger
from pydantic import BaseModel
from decouple import config


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
    @staticmethod
    def api_key():
        return config("GOOGLE_API_KEY")

    @staticmethod
    def tools():
        return [{"google_search": {}}]

    @staticmethod
    def response_format():
        return Questions.model_json_schema()

    @classmethod
    def get_config(cls):
        return {
            "tools": cls.tools(),
            "response_format": {
                "text": {
                    "mime_type": "application/json",
                    "schema": cls.response_format(),
                },
            },
        }


class GeminiAgent:
    def __init__(self, config: dict, logger: Logger, key: str):
        self.config = config
        self.logger = logger
        self.client = self.get_client(key)
        self.logger.info(f"Initialized GeminiAgent with config: {self.config}")

    def get_client(self, key: str):
        return genai.Client(api_key=key)

    def get_chat(self):
        self.client.chats.create()
