import asyncio
import json
from logging import getLogger
from collections.abc import Generator
from time import sleep
from google import genai
from google.genai import types
from decouple import config
from core.types import Questions, Question, answers_serializer


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

logger = getLogger(__name__)


class GeminiConfig:
    INSTRUCTION = """
    You are a helpful assistant for students. You generate questions based on the provided text.
    Do not use information from outside of the provided text. Generate 5 questions with 4 answer options for each question.
    The answer options should be labeled with letters A, B, C, D. Provide the correct answer letter for each question. 
    """
    IMAGE_INSTRUCTION = """
    Ти — експерт з аналізу навчальних матеріалів. Проаналізуй зображення та витягни всю інформацію, 
    яка може знадобитися для створення тестів. Не описуй оформлення, кольори або розташування елементів, 
    якщо вони не мають навчального значення.\n\nПоверни результат у структурованому вигляді:\n\n1. 
    Основна тема зображення.\n2. Усі ключові поняття та їх визначення.\n3. 
    Усі факти, правила, закони, властивості та твердження.\n4. Усі формули, позначення та пояснення змінних.\n5.
    Усі етапи процесів, алгоритмів або послідовностей дій.\n6. Усі зв’язки між об’єктами 
    (причина-наслідок, порівняння, залежності, класифікації).\n7. Усі числові значення, дати, одиниці вимірювання 
    та важливі характеристики.\n8. Якщо є таблиці — перепиши всі рядки, стовпці та їхній зміст.\n9. Якщо є діаграми, 
    схеми або графіки — поясни, що вони показують і які висновки з них можна зробити.\n10. Переліч усі терміни, які 
    зустрічаються на зображенні.\n11. Вкажи нечіткі, погано читані або неоднозначні елементи.\n\nГоловна мета — 
    отримати максимум навчальної інформації, яку можна використати для генерації тестових питань з однією правильною відповіддю. 
    Не додавай інформацію, якої немає на зображенні.
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

    @classmethod
    def get_image_config(cls):
        return {"type": "text", "text": cls.IMAGE_INSTRUCTION}


class GeminiAgent:
    CHUNKS_SIZE = 1000

    def __init__(self, config: types.GenerateContentConfig, image_config: dict):
        self.config = config
        self.image_config = image_config
        self.client = self.get_client()
        self.model = "gemini-3.5-flash"

    @staticmethod
    def get_client():
        return genai.Client(api_key=GeminiConfig.api_key())

    @staticmethod
    def divide_into_chunks(text: str):
        for i in range(0, len(text), GeminiAgent.CHUNKS_SIZE):
            yield text[i : i + GeminiAgent.CHUNKS_SIZE]

    def generate_tasks(
        self,
        chunks: Generator[str, None, None],
        chat_id: int,
    ):
        questions = asyncio.run(self._generate_tasks(chunks=chunks))
        self.save_questions(questions=questions, chat_id=chat_id)

    async def _generate_tasks(
        self, chunks: Generator[str, None, None]
    ) -> list[Question]:
        async with asyncio.TaskGroup() as tg:
            tasks: list[asyncio.Task] = []
            for chunk in chunks:
                tasks.append(
                    tg.create_task(asyncio.to_thread(self._generate_question, chunk))
                )
        questions = []
        for task in tasks:
            result = task.result()
            questions += result
        return questions

    def _generate_question(self, text: str) -> list[Question]:
        # response = self.client.models.generate_content(
        #     contents=text, model=self.model, config=self.config
        # )
        # text_response = response.text
        # dict_response = json.loads(text_response)
        dict_response = FAKE_RESPONSE  # temporary
        sleep(10)
        return Questions.model_validate(dict_response).questions

    def save_questions(self, questions: list[Question], chat_id: int):
        # TODO - move to service
        from questions.models import Question as QuestionModel

        question_objects = []
        for question in questions:
            answers = answers_serializer(question.answers)
            question_objects.append(
                QuestionModel(
                    chat_id=chat_id,
                    question_text=question.question,
                    correct_answer_letter=question.correct_answer_letter,
                    options=answers,
                )
            )
        QuestionModel.objects.bulk_create(question_objects)

    def generate_image_description(self, image_path: str) -> str:
        image = self.client.files.upload(file=image_path)
        interation = self.client.interactions.create(
            model=self.model,
            input=[
                self.image_config,
                {"type": "image", "uri": image.uri, "mime_type": image.mime_type},
            ],
        )
        return interation.output_text
