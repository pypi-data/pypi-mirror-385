from __future__ import annotations

from typing import TYPE_CHECKING

from specflow.core.exceptions import ValidationError

if TYPE_CHECKING:
    from specflow.typing import Object

    from .schema import Schema
    from .types import Boolean, Integer, Number, String


class Condition:
    def __init__(
        self,
        if_: Schema | String | Number | Integer | Boolean,
        then_: Schema | String | Number | Integer | Boolean,
        else_: Schema | String | Number | Integer | Boolean | None = None,
    ) -> None:
        self._if: Schema | String | Number | Integer | Boolean = if_
        self._else: Schema | String | Number | Integer | Boolean | None = else_
        self._then: Schema | String | Number | Integer | Boolean = then_

    def __call__(self, to_validate: Object) -> None:
        if (if_title := self._if.title) not in to_validate:
            raise ValidationError(
                f"Required condition field '{if_title}' not found in data",
            )

        try:
            try:
                self._if(to_validate[if_title])  # type: ignore
            except ValidationError as e:
                raise e.add_path(if_title) from None

            try:
                self._then(to_validate[self._then.title])  # type: ignore
            except ValidationError as e:
                raise e.add_path(self._then.title) from None

        except ValidationError:
            if self._else and (else_title := self._else.title) in to_validate:
                try:
                    self._else(to_validate[else_title])  # type: ignore
                except ValidationError as e:
                    raise e.add_path(else_title) from None
            else:
                raise

    def to_dict(self) -> Object:
        data: Object = {"if": self._if.to_dict()}

        if self._else:
            data["else"] = self._else.to_dict()

        if self._then:
            data["then"] = self._then.to_dict()

        return data
