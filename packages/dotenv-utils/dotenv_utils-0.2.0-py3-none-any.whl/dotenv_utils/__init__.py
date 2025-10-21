"""
This package contains utility functions for parsing values from the environment.
"""

from __future__ import annotations

from os import environ
from typing import Any, Callable, TypeVar

T = TypeVar("T")


def get_var(
        name: str,
        default: T | Any = ...,  # ellipsis acts as sentinel value
        cast: Callable[[str], T] = str,  # type: ignore[assignment]
) -> T:
    """
    Retrieve an environment variable, and raise if it's undefined and no default was passed.

    :param name: The name of the environment variable.
    :param default: The default value to return if the environment variable is not defined. \
                    If nothing is passed, undefined variables raise an exception.
    :param cast: A function to cast the value to a specific type. Default is ``str``.
    :raise RuntimeError: If the environment variable is not defined and no default was provided.
    :return: The value of the environment variable cast to type by the specified function.
    """
    if default is not ...:
        default_list: list[T] | Any = [default]
    else:
        default_list = ...
    [value] = get_var_list(name, default=default_list, cast=cast, sep=None)
    return value


def get_var_list(
        name: str,
        default: list[T] | Any = ...,  # ellipsis acts as sentinel value
        cast: Callable[[str], T] = str,  # type: ignore[assignment]
        sep: str | None = ";"
) -> list[T]:
    """
    Retrieve a list of values from an environment variable, and raise if it's undefined and no default was passed.

    :param name: The name of the environment variable.
    :param default: The default value to return if the environment variable is not defined. \
                    If nothing is passed, undefined variables raise an exception.
    :param cast: A function to cast values to a specific type. Default is ``str``.
    :param sep: The seperator to use between values. Default is ``;``. Pass ``None`` to avoid splitting.
    :raise RuntimeError: If the environment variable is not defined and no default was provided.
    :return: The value of the environment variable cast to type by the specified function.
    """
    try:
        raw_value = environ[name]
    except KeyError as e:
        if default is ...:
            raise RuntimeError(f'Environment variable "{name}" is undefined and no default was provided.') from e
        else:
            return default

    # None indicates no list treatment
    if sep is None:
        raw_values = [raw_value]
    else:
        raw_values = raw_value.split(sep)

    values = []
    for raw_value in raw_values:
        value = cast(raw_value.strip())
        values.append(value)

    return values
