from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Iterable, Iterator, SupportsIndex, TypeAlias

from typing_extensions import TypeIs

from .supports import SupportsString

__all__ = ["Sentinel", "SentinelT", "StrList"]


class StrList(list[SupportsString]):
    """Custom class for representing a recursively "stringable" list."""

    if TYPE_CHECKING:

        def __init__(self, iterable: Iterable[SupportsString | None] | None = ..., /) -> None: ...

    @property
    def string(self) -> str:
        return self.to_str()

    def to_str(self) -> str:
        return str(self)

    def __str__(self) -> str:
        from ..functions import flatten

        return " ".join(filter(None, (str(x).strip() for x in flatten(self) if x is not None)))

    def __add__(self, x: list[SupportsString]) -> StrList:  # type: ignore[override]
        return StrList(super().__add__(x))

    def __mul__(self, n: SupportsIndex) -> StrList:
        return StrList(super().__mul__(n))

    def __rmul__(self, n: SupportsIndex) -> StrList:
        return StrList(super().__rmul__(n))

    @property
    def mlength(self) -> int:
        return len(self) - 1

    def append(self, *__object: SupportsString) -> None:
        for __obj in __object:
            super().append(__obj)


class SentinelDispatcher:
    def check[T](self, ret_value: T, cond: bool) -> T | SentinelDispatcher:
        return ret_value if cond else self

    def check_cb[T, **P](self, callback: Callable[P, tuple[T, bool]]) -> Callable[P, T | SentinelDispatcher]:
        @wraps(callback)
        def _wrap(*args: P.args, **kwargs: P.kwargs) -> T | SentinelDispatcher:
            return self.check(*callback(*args, **kwargs))

        return _wrap

    def filter[T](self, items: Iterable[T | SentinelDispatcher]) -> Iterator[T]:
        for item in items:
            if isinstance(item, SentinelDispatcher):
                continue
            yield item

    @classmethod
    def filter_multi[T](cls, items: Iterable[T | SentinelDispatcher], *sentinels: SentinelDispatcher) -> Iterator[T]:
        def _in_sentinels(it: Any) -> TypeIs[SentinelDispatcher]:
            return it in sentinels

        for item in items:
            if _in_sentinels(item):
                continue

            yield item

    def __getattr__(self, name: str) -> SentinelDispatcher:
        if name not in _sentinels:
            _sentinels[name] = SentinelDispatcher()
        return _sentinels[name]

    def __setattr__(self, name: str, value: Any) -> None:
        raise NameError

    def __call__(self) -> SentinelDispatcher:
        return SentinelDispatcher()


Sentinel = SentinelDispatcher()
SentinelT: TypeAlias = SentinelDispatcher

_sentinels = dict[str, SentinelDispatcher]()
