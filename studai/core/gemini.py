from logging import Logger
from chat.services.gemini import GeminiAgent, GeminiConfig


class Gemini:
    agent = None

    @classmethod
    def get_agent(cls, logger: Logger):
        if not cls.agent:
            cls.agent = GeminiAgent(
                config=GeminiConfig.get_config(),
                logger=logger,
                image_config=GeminiConfig.get_image_config(),
            )
        return cls.agent
