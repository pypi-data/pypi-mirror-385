from typing import Literal

from pydantic import Field, field_validator
from whenever import ZonedDateTime

from hassette.utils.date_utils import convert_datetime_str_to_system_tz

from .base import AttributesBase, StringBaseState


class ScriptState(StringBaseState):
    class Attributes(AttributesBase):
        last_triggered: ZonedDateTime | None = Field(default=None)
        mode: str | None = Field(default=None)
        current: int | float | None = Field(default=None)

        @field_validator("last_triggered", mode="before")
        @classmethod
        def parse_last_triggered(cls, value: ZonedDateTime | str | None) -> ZonedDateTime | None:
            return convert_datetime_str_to_system_tz(value)

    domain: Literal["script"]

    attributes: Attributes
