from __future__ import annotations

import collections.abc
import types
import typing

import amulet.utils.lock

__all__: list[str] = ["IdRegistry"]

class IdRegistry:
    """
    A registry for namespaced ids.
    External synchronisation is required with this class.
    """

    def __contains__(self, item: typing.SupportsInt) -> bool: ...
    def __eq__(self, other: typing.Any) -> bool | types.NotImplementedType: ...
    @typing.overload
    def __getitem__(self, index: typing.SupportsInt) -> tuple[str, str]:
        """
        Convert a numerical id to its namespaced id.
        External shared lock required.
        """

    @typing.overload
    def __getitem__(self, name: tuple[str, str]) -> int:
        """
        Convert a namespaced id to its numerical id.
        External shared lock required.
        """

    def __hash__(self) -> int: ...
    def __init__(self) -> None: ...
    def __iter__(self) -> collections.abc.Iterator[int]:
        """
        An iterable of the numerical ids registered.
        External shared lock required.
        """

    def __len__(self) -> int:
        """
        The number of ids registered.
        External shared lock required.
        """

    @typing.overload
    def get(self, key: typing.SupportsInt) -> tuple[str, str] | None: ...
    @typing.overload
    def get(
        self, key: typing.SupportsInt, default: tuple[str, str]
    ) -> tuple[str, str]: ...
    @typing.overload
    def get[T](self, key: typing.SupportsInt, default: T) -> tuple[str, str] | T: ...
    def items(self) -> collections.abc.ItemsView[int, tuple[str, str]]: ...
    def keys(self) -> collections.abc.KeysView[int]: ...
    @typing.overload
    def namespace_id_to_numerical_id(self, name: tuple[str, str]) -> int:
        """
        Convert a namespaced id to its numerical id.
        External shared lock required.
        """

    @typing.overload
    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int:
        """
        Convert a namespaced id to its numerical id.
        External shared lock required.
        """

    def numerical_id_to_namespace_id(
        self, index: typing.SupportsInt
    ) -> tuple[str, str]:
        """
        Convert a numerical id to its namespaced id.
        External shared lock required.
        """

    def register_id(self, index: typing.SupportsInt, name: tuple[str, str]) -> None:
        """
        Convert a namespaced id to its numerical id.
        External unique lock required.
        """

    def values(self) -> collections.abc.ValuesView[tuple[str, str]]: ...
    @property
    def lock(self) -> amulet.utils.lock.SharedLock:
        """
        The public lock.
        Thread safe.
        """
