from abc import ABC, abstractmethod
from typing import Self, Union


from telegram import Update
from telegram.ext import CallbackContext


from .command_meta import CommandMeta, ACTION, TITLE


class Command(ABC):
    """`Command` is base class for implementation handler of `Telegram-bot` command (like "/start")."""

    _title: Union[str, None] = None

    class Meta(CommandMeta): ...

    @classmethod
    def action(cls) -> str:
        __SLASH = "/"
        return f"{__SLASH}{getattr(cls.Meta, ACTION, cls.__name__.lower().lstrip(__SLASH))}"

    def get_title(self) -> str:
        if getattr(self, "_title", None):
            return getattr(self, "_title")
        if getattr(self.Meta, TITLE, None):
            return f"{getattr(self.Meta, TITLE)}"
        return self.__class__.__name__

    def set_title(self, title: str) -> Self:
        self._title = title
        return self

    @abstractmethod
    async def on_call(
        self,
        update: Update,
        context: CallbackContext,
    ):
        """Reaction of User call command like by /command"""
        ...
