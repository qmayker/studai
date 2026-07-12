from functools import wraps
from websocket.types.socket import ChannelMessage


def modifying(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._session.modified = True
        return result

    return wrapper


def channel_send(func_name: str = "_send_to_channel"):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result: ChannelMessage = func(self, *args, **kwargs)
            getattr(self, func_name)(result)
            return result

        return wrapper

    return decorator
