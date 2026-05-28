class WebSocketServices:
    @staticmethod
    def get_group_name(chat_id: int | str) -> str:
        return f"chat_{chat_id}"
