import importlib
import inspect
import pkgutil
from collections.abc import Callable, Iterator

import pytest

import celery.utils


def _utils_modules() -> list:
    modules = [celery.utils]
    for module_info in pkgutil.walk_packages(celery.utils.__path__, 'celery.utils.'):
        modules.append(importlib.import_module(module_info.name))
    return modules


def _class_methods(cls: type) -> Iterator[tuple[str, Callable]]:
    for attr, member in vars(cls).items():
        if attr.startswith('_'):
            continue
        if isinstance(member, (staticmethod, classmethod)):
            member = member.__func__
        elif isinstance(member, property):
            member = member.fget
        # Skip aliases such as ``keys = _iterate_keys``: the alias's own definition is checked.
        if inspect.isfunction(member) and member.__name__ == attr:
            yield f'{cls.__name__}.{attr}', member


def _public_callables(module) -> Iterator[tuple[str, Callable]]:
    for name, obj in vars(module).items():
        if getattr(obj, '__module__', None) != module.__name__:
            continue
        if inspect.isclass(obj):
            yield from _class_methods(obj)
        elif not name.startswith('_') and (inspect.isfunction(obj) or hasattr(obj, '__wrapped__')):
            yield name, obj


def _unannotated_parameters(func: Callable) -> list[str]:
    signature = inspect.signature(func)
    missing = [
        name for name, param in signature.parameters.items()
        if param.annotation is param.empty and name not in ('self', 'cls')
    ]
    if signature.return_annotation is signature.empty:
        missing.append('return')
    return missing


@pytest.mark.parametrize('module', _utils_modules(), ids=lambda module: module.__name__)
def test_public_callables_are_annotated(module) -> None:
    unannotated = {}
    for qualname, func in _public_callables(module):
        missing = _unannotated_parameters(func)
        if missing:
            unannotated[qualname] = missing
    assert unannotated == {}
