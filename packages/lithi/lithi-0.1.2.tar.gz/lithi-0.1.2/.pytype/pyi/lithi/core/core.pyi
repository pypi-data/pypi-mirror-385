# (generated with --quick)

import functools
from typing import Any, Callable, ParamSpec, Sequence, TypeVar

_instances: dict[type, Any]

_PWrapped = ParamSpec('_PWrapped')
_RWrapped = TypeVar('_RWrapped')
_T = TypeVar('_T')

def singleton(cls: type[_T]) -> type[_T]: ...
def wraps(wrapped: Callable[_PWrapped, _RWrapped], assigned: Sequence[str] = ..., updated: Sequence[str] = ...) -> functools._Wrapper[_PWrapped, _RWrapped]: ...
