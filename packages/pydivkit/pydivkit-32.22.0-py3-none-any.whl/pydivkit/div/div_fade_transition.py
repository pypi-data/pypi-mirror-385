# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_animation_interpolator


# Transparency animation.
class DivFadeTransition(BaseDiv):

    def __init__(
        self, *,
        type: str = "fade",
        alpha: typing.Optional[typing.Union[Expr, float]] = None,
        duration: typing.Optional[typing.Union[Expr, int]] = None,
        interpolator: typing.Optional[typing.Union[Expr, div_animation_interpolator.DivAnimationInterpolator]] = None,
        start_delay: typing.Optional[typing.Union[Expr, int]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            alpha=alpha,
            duration=duration,
            interpolator=interpolator,
            start_delay=start_delay,
            **kwargs,
        )

    type: str = Field(default="fade")
    alpha: typing.Optional[typing.Union[Expr, float]] = Field(
        description=(
            "Value of the alpha channel which the element starts "
            "appearing from or at which itfinishes disappearing."
        ),
    )
    duration: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Animation duration in milliseconds.",
    )
    interpolator: typing.Optional[typing.Union[Expr, div_animation_interpolator.DivAnimationInterpolator]] = Field(
        description="Transition speed nature.",
    )
    start_delay: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Delay in milliseconds before animation starts.",
    )


DivFadeTransition.update_forward_refs()
