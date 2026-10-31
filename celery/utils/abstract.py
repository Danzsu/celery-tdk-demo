"""Abstract classes."""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from typing import Any, TypeVar

__all__ = ('CallableTask', 'CallableSignature')

_T = TypeVar('_T')


def _hasattr(C, attr):
    return any(attr in B.__dict__ for B in C.__mro__)


class _AbstractClass(metaclass=ABCMeta):
    __required_attributes__ = frozenset()

    @classmethod
    def _subclasshook_using(cls, parent, C):
        return (
            cls is parent and
            all(_hasattr(C, attr) for attr in cls.__required_attributes__)
        ) or NotImplemented

    @classmethod
    def register(cls, other: _T) -> _T:
        # we override `register` to return other for use as a decorator.
        type(cls).register(cls, other)
        return other


class CallableTask(_AbstractClass, Callable):  # pragma: no cover
    """Task interface."""

    __required_attributes__ = frozenset({
        'delay', 'apply_async', 'apply',
    })

    @abstractmethod
    def delay(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def apply_async(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @abstractmethod
    def apply(self, *args: Any, **kwargs: Any) -> Any:
        pass

    @classmethod
    def __subclasshook__(cls, C):
        return cls._subclasshook_using(CallableTask, C)


class CallableSignature(CallableTask):  # pragma: no cover
    """Celery Signature interface."""

    __required_attributes__ = frozenset({
        'clone', 'freeze', 'set', 'link', 'link_error', '__or__',
    })

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def type(self) -> Any:
        pass

    @property
    @abstractmethod
    def app(self) -> Any:
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def task(self) -> str:
        pass

    @property
    @abstractmethod
    def args(self) -> tuple[Any, ...]:
        pass

    @property
    @abstractmethod
    def kwargs(self) -> dict[str, Any]:
        pass

    @property
    @abstractmethod
    def options(self) -> dict[str, Any]:
        pass

    @property
    @abstractmethod
    def subtask_type(self) -> str | None:
        pass

    @property
    @abstractmethod
    def chord_size(self) -> int | None:
        pass

    @property
    @abstractmethod
    def immutable(self) -> bool:
        pass

    @abstractmethod
    def clone(
        self,
        args: Sequence[Any] | None = None,
        kwargs: Mapping[str, Any] | None = None,
    ) -> CallableSignature:
        pass

    @abstractmethod
    def freeze(self, id: str | None = None, group_id: str | None = None, chord: Any = None,
               root_id: str | None = None, group_index: int | None = None) -> Any:
        pass

    @abstractmethod
    def set(self, immutable: bool | None = None, **options: Any) -> CallableSignature:
        pass

    @abstractmethod
    def link(self, callback: Any) -> Any:
        pass

    @abstractmethod
    def link_error(self, errback: Any) -> Any:
        pass

    @abstractmethod
    def __or__(self, other):
        pass

    @abstractmethod
    def __invert__(self):
        pass

    @classmethod
    def __subclasshook__(cls, C):
        return cls._subclasshook_using(CallableSignature, C)
