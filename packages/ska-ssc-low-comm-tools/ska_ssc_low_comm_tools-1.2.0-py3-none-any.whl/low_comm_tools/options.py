from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T", bound=BaseModel)


class BaseOptions(BaseModel):
    """A base class that Options style flint classes can
    inherit from. This is derived from ``pydantic.BaseModel``,
    and can be used for validation of supplied values.

    Class derived from ``BaseOptions`` are immutable by
    default, and have the docstrings of attributes
    extracted.
    """

    model_config = ConfigDict(
        frozen=True,
        from_attributes=True,
        use_attribute_docstrings=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    def with_options(self: T, /, **kwargs) -> T:  # type: ignore[no-untyped-def]
        new_args = self.__dict__.copy()
        new_args.update(**kwargs)

        return self.__class__(**new_args)

    def _asdict(self) -> dict[str, Any]:
        return self.__dict__
