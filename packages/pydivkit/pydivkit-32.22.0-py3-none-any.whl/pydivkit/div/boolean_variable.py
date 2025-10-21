# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field


# A Boolean variable in binary format.
class BooleanVariable(BaseDiv):

    def __init__(
        self, *,
        type: str = "boolean",
        name: typing.Optional[typing.Union[Expr, str]] = None,
        value: typing.Optional[typing.Union[Expr, bool]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            name=name,
            value=value,
            **kwargs,
        )

    type: str = Field(default="boolean")
    name: typing.Union[Expr, str] = Field(
        description="Variable name.",
    )
    value: typing.Union[Expr, bool] = Field(
        description="Value. Supports expressions for variable initialization.",
    )


BooleanVariable.update_forward_refs()
