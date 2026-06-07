from functools import wraps


def modifying(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._session.modified = True
        return result

    return wrapper
