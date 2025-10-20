from __future__ import annotations

import os
import re
import inspect
import functools
from typing import (
    Any,
    Tuple,
    Mapping,
    TypeVar,
    Callable,
    Iterable,
    Sequence,
    cast,
    overload,
)
from pathlib import Path
from typing_extensions import TypeGuard


_T = TypeVar("_T")
_TupleT = TypeVar("_TupleT", bound=Tuple[object, ...])
_MappingT = TypeVar("_MappingT", bound=Mapping[str, object])
_SequenceT = TypeVar("_SequenceT", bound=Sequence[object])
CallableT = TypeVar("CallableT", bound=Callable[..., Any])


def flatten(t: Iterable[Iterable[_T]]) -> list[_T]:
    return [item for sublist in t for item in sublist]


# Type safe methods for narrowing types with TypeVars.
# The default narrowing for isinstance(obj, dict) is dict[unknown, unknown],
# however this cause Pyright to rightfully report errors. As we know we don't
# care about the contained types we can safely use `object` in it's place.
#
# There are two separate functions defined, `is_*` and `is_*_t` for different use cases.
# `is_*` is for when you're dealing with an unknown input
# `is_*_t` is for when you're narrowing a known union type to a specific subset


def is_tuple(obj: object) -> TypeGuard[tuple[object, ...]]:
    return isinstance(obj, tuple)


def is_tuple_t(obj: _TupleT | object) -> TypeGuard[_TupleT]:
    return isinstance(obj, tuple)


def is_sequence(obj: object) -> TypeGuard[Sequence[object]]:
    return isinstance(obj, Sequence)


def is_sequence_t(obj: _SequenceT | object) -> TypeGuard[_SequenceT]:
    return isinstance(obj, Sequence)


def is_mapping(obj: object) -> TypeGuard[Mapping[str, object]]:
    return isinstance(obj, Mapping)


def is_mapping_t(obj: _MappingT | object) -> TypeGuard[_MappingT]:
    return isinstance(obj, Mapping)


def is_dict(obj: object) -> TypeGuard[dict[object, object]]:
    return isinstance(obj, dict)


def is_list(obj: object) -> TypeGuard[list[object]]:
    return isinstance(obj, list)


def is_iterable(obj: object) -> TypeGuard[Iterable[object]]:
    return isinstance(obj, Iterable)


def deepcopy_minimal(item: _T) -> _T:
    """Minimal reimplementation of copy.deepcopy() that will only copy certain object types:

    - mappings, e.g. `dict`
    - list

    This is done for performance reasons.
    """
    if is_mapping(item):
        return cast(_T, {k: deepcopy_minimal(v) for k, v in item.items()})
    if is_list(item):
        return cast(_T, [deepcopy_minimal(entry) for entry in item])
    return item


# copied from https://github.com/Rapptz/RoboDanny
def human_join(seq: Sequence[str], *, delim: str = ", ", final: str = "or") -> str:
    size = len(seq)
    if size == 0:
        return ""

    if size == 1:
        return seq[0]

    if size == 2:
        return f"{seq[0]} {final} {seq[1]}"

    return delim.join(seq[:-1]) + f" {final} {seq[-1]}"


def quote(string: str) -> str:
    """Add single quotation marks around the given string. Does *not* do any escaping."""
    return f"'{string}'"


def required_args(*variants: Sequence[str]) -> Callable[[CallableT], CallableT]:
    """Decorator to enforce a given set of arguments or variants of arguments are passed to the decorated function.

    Useful for enforcing runtime validation of overloaded functions.

    Example usage:
    ```py
    @overload
    def foo(*, a: str) -> str:
        ...


    @overload
    def foo(*, b: bool) -> str:
        ...


    # This enforces the same constraints that a static type checker would
    # i.e. that either a or b must be passed to the function
    @required_args(["a"], ["b"])
    def foo(*, a: str | None = None, b: bool | None = None) -> str:
        ...
    ```
    """

    def inner(func: CallableT) -> CallableT:
        params = inspect.signature(func).parameters
        positional = [
            name
            for name, param in params.items()
            if param.kind
            in {
                param.POSITIONAL_ONLY,
                param.POSITIONAL_OR_KEYWORD,
            }
        ]

        @functools.wraps(func)
        def wrapper(*args: object, **kwargs: object) -> object:
            given_params: set[str] = set()
            for i, _ in enumerate(args):
                try:
                    given_params.add(positional[i])
                except IndexError:
                    raise TypeError(
                        f"{func.__name__}() takes {len(positional)} argument(s) but {len(args)} were given"
                    ) from None

            for key in kwargs.keys():
                given_params.add(key)

            for variant in variants:
                matches = all((param in given_params for param in variant))
                if matches:
                    break
            else:  # no break
                if len(variants) > 1:
                    variations = human_join(
                        [
                            "("
                            + human_join([quote(arg) for arg in variant], final="and")
                            + ")"
                            for variant in variants
                        ]
                    )
                    msg = f"Missing required arguments; Expected either {variations} arguments to be given"
                else:
                    assert len(variants) > 0

                    # TODO: this error message is not deterministic
                    missing = list(set(variants[0]) - given_params)
                    if len(missing) > 1:
                        msg = f"Missing required arguments: {human_join([quote(arg) for arg in missing])}"
                    else:
                        msg = f"Missing required argument: {quote(missing[0])}"
                raise TypeError(msg)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return inner


_K = TypeVar("_K")
_V = TypeVar("_V")


def coerce_integer(val: str) -> int:
    return int(val, base=10)


def coerce_float(val: str) -> float:
    return float(val)


def coerce_boolean(val: str) -> bool:
    return val == "true" or val == "1" or val == "on"


def maybe_coerce_integer(val: str | None) -> int | None:
    if val is None:
        return None
    return coerce_integer(val)


def maybe_coerce_float(val: str | None) -> float | None:
    if val is None:
        return None
    return coerce_float(val)


def maybe_coerce_boolean(val: str | None) -> bool | None:
    if val is None:
        return None
    return coerce_boolean(val)


def removeprefix(string: str, prefix: str) -> str:
    """Remove a prefix from a string.

    Backport of `str.removeprefix` for Python < 3.9
    """
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


def removesuffix(string: str, suffix: str) -> str:
    """Remove a suffix from a string.

    Backport of `str.removesuffix` for Python < 3.9
    """
    if string.endswith(suffix):
        return string[: -len(suffix)]
    return string


def lru_cache(*, maxsize: int | None = 128) -> Callable[[CallableT], CallableT]:
    """A version of functools.lru_cache that retains the type signature
    for the wrapped function arguments.
    """
    wrapper = functools.lru_cache(  # noqa: TID251
        maxsize=maxsize,
    )
    return cast(Any, wrapper)  # type: ignore[no-any-return]
