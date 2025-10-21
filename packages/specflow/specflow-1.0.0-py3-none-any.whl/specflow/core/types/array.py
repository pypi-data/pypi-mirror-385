from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar, cast

from specflow.core.exceptions import ValidationError

E = TypeVar(
    "E",
    str,
    int,
    float,
    bool,
    None,
)


T = TypeVar(
    "T",
    str,
    int,
    float,
    bool,
)

if TYPE_CHECKING:
    from specflow.core.schema import Schema
    from specflow.typing import Object

    from .boolean import Boolean
    from .integer import Integer
    from .number import Number
    from .string import String


class ArrayConstraint(ABC):
    @property
    @abstractmethod
    def _name(self) -> str: ...

    @property
    @abstractmethod
    def _value(self) -> list[E]: ...

    @abstractmethod
    def __call__(self, to_validate: list[Object] | None) -> None: ...

    def to_dict(self) -> Object:
        return {self._name: self._value}  # type: ignore


class Array:
    def __init__(
        self,
        title: str,
        description: str | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        min_contains: int | None = None,
        max_contains: int | None = None,
        items: String | Number | Integer | Boolean | Schema | None = None,
        prefix_items: list[String | Number | Integer | Boolean | Schema] | None = None,
        *,
        nullable: bool = False,
    ) -> None:
        self._title: str = title
        self._description: str | None = description
        self._items: String | Number | Integer | Boolean | Schema | None = items
        self._prefix_items: (
            list[String | Number | Integer | Boolean | Schema] | None
        ) = prefix_items
        self._min_items: int | None = min_items
        self._max_items: int | None = max_items
        self._min_contains: int | None = min_contains
        self._max_contains: int | None = max_contains
        self._nullable: bool = nullable

    @property
    def _type(self) -> str:
        return "array"

    @property
    def title(self) -> str:
        return self._title

    def __call__(self, to_validate: list[Object] | None) -> None:  # noqa: C901, PLR0912
        if self._min_items is not None:
            MinItems(self._min_items)(to_validate)
        if self._max_items is not None:
            MaxItems(self._max_items)(to_validate)
        if self._min_contains is not None:
            MinContains(self._min_contains)(to_validate)
        if self._max_contains is not None:
            MaxContains(self._max_contains)(to_validate)

        if to_validate is not None:
            if self._prefix_items is not None:
                for i, (value, schema) in enumerate(
                    zip(to_validate, self._prefix_items, strict=False),
                ):
                    try:
                        schema(value)  # type: ignore
                    except ValidationError as e:  # noqa: PERF203
                        raise e.add_path(i) from None

                if self._items is not None and len(to_validate) > len(
                    self._prefix_items,
                ):
                    for i in range(len(self._prefix_items), len(to_validate)):
                        try:
                            self._items(to_validate[i])  # type: ignore
                        except ValidationError as e:  # noqa: PERF203
                            raise e.add_path(i) from None

            elif self._items is not None:
                for i, value in enumerate(to_validate):
                    try:
                        self._items(value)  # type: ignore
                    except ValidationError as e:  # noqa: PERF203
                        raise e.add_path(i) from None

    def to_dict(self) -> Object:
        data: Object = {
            self.title: cast(
                "Object",
                {
                    "type": self._type,
                },
            ),
        }

        if self._description is not None:
            data["description"] = self._description

        if self._items is not None:
            data["items"] = self._items.to_dict()

        if self._prefix_items is not None:
            data["prefixItems"] = [item.to_dict() for item in self._prefix_items]

        return data


class MinItems(ArrayConstraint):
    def __init__(self, minimum: int) -> None:
        if minimum < 0:
            raise ValueError("'minimum' must be greater than or equal to 0.")

        self._minimum: int = minimum

    @property
    def _name(self) -> str:
        return "minItems"

    @property
    def _value(self) -> int:  # type: ignore
        return self._minimum

    def __call__(self, to_validate: list[Object] | None) -> None:
        if to_validate is None:
            return

        if (n := len(to_validate)) < self._minimum:
            raise ValidationError(
                f"Must have at least {self._minimum} items, got {n}",
            )


class MaxItems(ArrayConstraint):
    def __init__(self, maximum: int) -> None:
        if maximum < 0:
            raise ValueError(
                "'maximum' must be greater than or equal to 0.",
            )

        self._maximum: int = maximum

    @property
    def _name(self) -> str:
        return "maxItems"

    @property
    def _value(self) -> int:  # type: ignore
        return self._maximum

    def __call__(self, to_validate: list[Object] | None) -> None:
        if to_validate is None:
            return

        if (n := len(to_validate)) > self._maximum:
            raise ValidationError(
                f"Must have at most {self._maximum} items, got {n}",
            )


class MinContains(ArrayConstraint):
    def __init__(self, minimum: int) -> None:
        if minimum < 0:
            raise ValueError("'minimum' must be greater than or equal to 0.")

        self._minimum: int = minimum

    @property
    def _name(self) -> str:
        return "minContains"

    @property
    def _value(self) -> int:  # type: ignore
        return self._minimum

    def __call__(self, to_validate: list[Object] | None) -> None:
        if to_validate is None:
            return

        if (n := len(to_validate)) < self._minimum:
            raise ValidationError(
                f"Must contain at least {self._minimum} matching items, got {n}",
            )


class MaxContains(ArrayConstraint):
    def __init__(self, maximum: int) -> None:
        if maximum < 0:
            raise ValueError(
                "'maximum' must be greater than or equal to 0.",
            )

        self._maximum: int = maximum

    @property
    def _name(self) -> str:
        return "maxContains"

    @property
    def _value(self) -> int:  # type: ignore
        return self._maximum

    def __call__(self, to_validate: list[Object] | None) -> None:
        if to_validate is None:
            return

        if (n := len(to_validate)) > self._maximum:
            raise ValidationError(
                f"Must contain at most {self._maximum} matching items, got {n}",
            )
