from typing import Any
from abc import abstractmethod, ABC
from logging import getLogger

logger = getLogger(__name__)


class RedisLockKwargs(ABC):
    @staticmethod
    @abstractmethod
    def key() -> str: ...

    @staticmethod
    def _default_kwargs():
        return {"expire": 30}

    @classmethod
    def get_kwargs(cls, *args, **kwargs) -> str:
        name = cls.add_args(*args, name=cls.key())
        logger.info(f"{args, kwargs, name}")
        return cls._get_kwargs(name=name, kwargs=kwargs)

    @staticmethod
    def add_args(*args: str | int, name: str):
        for arg in args:
            name = f"{name}:{arg}"
        return name

    @classmethod
    def _get_kwargs(cls, name: str, kwargs: dict[str, Any]) -> dict:
        default_kwargs = cls._default_kwargs()
        default_kwargs.update(kwargs)
        default_kwargs["name"] = name
        return default_kwargs


class TestResultKwargs(RedisLockKwargs):
    @staticmethod
    def key():
        return "quiz:result"


class QuestionGeneratingKwargs(RedisLockKwargs):
    @staticmethod
    def key():
        return "question:generating"


class DescriptionGeneratingKwargs(RedisLockKwargs):
    @staticmethod
    def key():
        return "description:generating"


class TaskRestoringKwargs(RedisLockKwargs):
    @staticmethod
    def key():
        return "task-restoring"
