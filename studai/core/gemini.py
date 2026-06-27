from logging import Logger
from chat.services.gemini import GeminiAgent, GeminiConfig


class Gemini:
    @staticmethod
    def get_agent(logger: Logger):
        return GeminiAgent(
            config=GeminiConfig.get_config(),
            logger=logger,
            image_config=GeminiConfig.get_image_config(),
        )
