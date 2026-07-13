from chat.services.gemini import GeminiAgent, GeminiConfig


class Gemini:
    @staticmethod
    def get_agent():
        return GeminiAgent(
            config=GeminiConfig.get_config(),
            image_config=GeminiConfig.get_image_config(),
        )
