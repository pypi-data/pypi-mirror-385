"""
Base data-model.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from datetime import date
from functools import reduce
from typing import TYPE_CHECKING, ClassVar, Optional, TypeVar, overload

import pydantic as pydantic
from pydantic import ConfigDict, RootModel
from typing_extensions import override

if TYPE_CHECKING:
    from IPython.lib.pretty import RepresentationPrinter


class BaseModel(pydantic.BaseModel, Mapping[str, object]):  # type: ignore[reportUnsafeMultipleInheritance]
    """Base data-model with mapping methods."""

    __slots__: tuple[str, str] = ("_owner", "_name")
    _owner: Optional["BaseModel"] = None
    _name: Optional[str] = None
    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_default=True,
        validate_assignment=True,
        use_enum_values=True,
    )

    def __init__(self, _owner: Optional["BaseModel"] = None, _name: Optional[str] = None, **kwargs: object) -> None:
        """Initialise model."""
        super().__init__(**kwargs)

        self._set_owner(_owner, _name)

        # take ownership of model fields
        for name, value in self.items():
            if isinstance(value, BaseModel):
                value._set_owner(self, name)
            elif isinstance(value, list):
                for x in value:  # type: ignore[any]
                    if not isinstance(x, BaseModel):
                        break
                    x._set_owner(self, name)

    def _set_owner(self, owner: Optional["BaseModel"], name: Optional[str] = None) -> None:
        """Set owner of object."""

        object.__setattr__(self, "_owner", owner)
        object.__setattr__(self, "_name", name)

    @override
    def __setattr__(self, name: str, value: object) -> None:
        """Set attribute."""

        super().__setattr__(name, value)

        result: Optional[object] = getattr(self, name)  # type: ignore[any]

        if isinstance(result, BaseModel):
            result._set_owner(self, name)
        elif isinstance(result, list):
            for x in result:  # type: ignore[any]
                if not isinstance(x, BaseModel):
                    break
                x._set_owner(self, name)

    @override
    def __getitem__(self, name: str) -> object:
        """Get item."""

        if "." in name:
            try:
                return reduce(lambda x, y: x[y], name.split("."), self)  # type: ignore[any, arg-type, return-value]
            except KeyError:
                raise KeyError(name) from None

        try:
            return getattr(self, name)  # type: ignore[any]
        except AttributeError:
            raise KeyError(name) from None

    def __setitem__(self, name: str, value: object) -> None:
        """Set item."""

        if "." not in name:
            setattr(self, name, value)
            return

        head_path, tail = name.rsplit(".", 1)
        head = self[head_path]

        setattr(head, tail, value)

    @override
    def __len__(self) -> int:
        """Number of keys."""

        return len(self.__dict__)

    def __iter__(self) -> Iterator[str]:  # type: ignore[override]
        """Key iterator."""

        return iter(self.__dict__)

    def _items_pretty_(self) -> Iterable[tuple[str, object]]:
        """Pretty items list."""

        return self.items()

    def _repr_pretty_(self, p: RepresentationPrinter, cycle: bool) -> None:
        """Pretty representation."""
        name = type(self).__name__
        if cycle:
            p.text(f"{name}(...)")  # type: ignore[any]
        else:
            with p.group(4, f"{name}(", ")"):
                for i, (k, v) in enumerate(self._items_pretty_()):
                    if i:
                        p.text(",")  # type: ignore[any]
                        p.breakable()
                    else:
                        p.breakable("")
                    p.text(f"{k}=")  # type: ignore[any]
                    p.pretty(v.isoformat() if isinstance(v, date) else v)  # type: ignore[any]


P = TypeVar("P")


class BaseModelRoot(RootModel[list[P]], Sequence[P]):  # type: ignore[reportUnsafeMultipleInheritance]
    """Base data-model with sequence methods."""

    root: list[P]
    model_config: ClassVar[ConfigDict] = ConfigDict(
        validate_default=True,
        validate_assignment=True,
    )

    def __init__(self, root: list[P]) -> None:
        super().__init__(root)  # type: ignore[any]

    @override
    def __str__(self) -> str:
        return str(self.root)

    @override
    def __eq__(self, other: object) -> bool:
        return self.root == other

    @override
    def __repr__(self) -> str:
        return repr(self.root)

    # Sequence methods
    @overload
    def __getitem__(self, item: int) -> P:
        """Get item by index."""
        ...

    @overload
    def __getitem__(self, item: slice) -> list[P]:
        """Get items by slice."""
        ...

    @override
    def __getitem__(self, item: int | slice) -> P | list[P]:
        """Get item(s)."""
        return self.root[item]

    @override
    def __len__(self) -> int:
        """Number of items."""

        return len(self.root)

    def __iter__(self) -> Iterator[P]:  # type: ignore[override]
        """Item iterator."""

        return iter(self.root)

    def _repr_pretty_(self, p: RepresentationPrinter, cycle: bool) -> None:
        """Pretty representation."""

        name = type(self).__name__
        if cycle:
            p.text(f"{name}[...]")  # type: ignore[any]
        else:
            with p.group(4, f"{name}[", "]"):
                for i, v in enumerate(self.root):
                    if i:
                        p.text(",")  # type: ignore[any]
                        p.breakable()
                    else:
                        p.breakable("")
                    _ = p.pretty(f"{v}" if isinstance(v, date) else v)  # type: ignore[any]
