#!/usr/bin/env python3


from typing import Awaitable, TypeVar, Union

T = TypeVar("T")
SyncAsync = Union[T, Awaitable[T]]