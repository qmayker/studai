from dataclasses import dataclass


@dataclass
class ChannelMessage:
    channel_id: str | None
    message: dict
