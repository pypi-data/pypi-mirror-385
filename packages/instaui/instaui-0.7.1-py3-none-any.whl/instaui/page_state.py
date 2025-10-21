from typing import ClassVar
from typing_extensions import Self
from contextvars import ContextVar


class PageState:
    _ctx: ClassVar[ContextVar["PageState"]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._ctx = ContextVar(f"{cls.__name__}_ctx")

    @classmethod
    def get(cls) -> Self:
        inst = cls._ctx.get(None)

        if inst is None:
            inst = cls()
            cls._ctx.set(inst)
        return inst  # type: ignore
