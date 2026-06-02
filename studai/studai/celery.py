import os
import channels.layers
from celery import Celery
from celery.app.log import get_logger
from chat.services.gemini import GeminiAgent, GeminiConfig

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studai.settings")

app = Celery("studai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

logger = get_logger(__name__)


@app.task()
def generate_questions(chat_id: int):
    agent = GeminiAgent(config=GeminiConfig.get_config(), logger=logger)

    chunks = agent.divide_into_chunks(
        "LLM models are large language models that can understand and generate human-like text based on the input they receive. They are trained on vast amounts of data and use deep learning techniques to learn patterns in language. LLMs can be used for various applications, such as chatbots, content generation, and language translation."
    )
    agent.generate_tasks(chunks, chat_id=chat_id)
