from __future__ import annotations

from pydantic import BaseModel, ValidationError

import typing as t
import click
import re

MAP_VALUE_RE = r"^(?P<key>.+)=(?P<value>.+)$"


class ClickMapping(click.ParamType):
    name = "mapping"

    def __init__(self, type_: t.Any) -> None:
        # pydantic will validate the input
        class Validator(BaseModel):
            field: type_

        self._model_validator = Validator

    def convert(
        self, value: t.Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> dict[str, t.Any]:
        parsed: dict[str, t.Any] = {}
        for pair in value.split(","):
            pair = pair.strip()
            match = re.match(MAP_VALUE_RE, pair)
            if match is None:
                continue
            k = match.group("key")
            v = match.group("value")
            parsed[k] = v

        if parsed:
            value = parsed

        try:
            if isinstance(value, dict):  # pragma: no cover
                self._model_validator(field=value)
                return value
            validated = self._model_validator.model_validate_json(
                '{"field":' + value + "}"
            )
            return validated.field  # type: ignore[no-any-return]
        except ValidationError as exc:
            first_violation = exc.errors(include_url=False, include_context=False)[0]
            self.fail(
                f"{value!r} is not a valid mapping. Pydantic validation error: msg={first_violation['msg']!r} path={first_violation['loc'][1:]!r} input={first_violation['input']!r}",
                param,
                ctx,
            )


class ClickList(click.ParamType):
    name = "list"

    def __init__(self, type_: t.Any) -> None:
        # pydantic will validate the input
        class Validator(BaseModel):
            field: type_

        self._model_validator = Validator

    def convert(
        self, value: t.Any, param: click.Parameter | None, ctx: click.Context | None
    ) -> list[t.Any]:
        # TODO: replace with regex matching
        if (
            isinstance(value, str)
            and not value.startswith("[")
            and not value.endswith("]")
        ):
            parsed = [item.strip() for item in value.split(",")]

            if parsed:
                value = parsed

        try:
            if isinstance(value, list):  # pragma: no cover
                self._model_validator(field=value)
                return value
            validated = self._model_validator.model_validate_json(
                '{"field":' + value + "}"
            )
            return validated.field  # type: ignore[no-any-return]
        except ValidationError as exc:
            first_violation = exc.errors(include_url=False, include_context=False)[0]
            self.fail(
                f"{value!r} is not a valid mapping. Pydantic validation error: msg={first_violation['msg']!r} path={first_violation['loc'][1:]!r} input={first_violation['input']!r}",
                param,
                ctx,
            )
