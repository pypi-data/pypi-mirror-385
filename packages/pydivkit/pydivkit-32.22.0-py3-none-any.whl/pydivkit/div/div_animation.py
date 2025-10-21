# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_animation_interpolator, div_count


# Element animation parameters.
class DivAnimation(BaseDiv):

    def __init__(
        self, *,
        duration: typing.Optional[typing.Union[Expr, int]] = None,
        end_value: typing.Optional[typing.Union[Expr, float]] = None,
        interpolator: typing.Optional[typing.Union[Expr, div_animation_interpolator.DivAnimationInterpolator]] = None,
        items: typing.Optional[typing.Sequence[DivAnimation]] = None,
        name: typing.Optional[typing.Union[Expr, DivAnimationName]] = None,
        repeat: typing.Optional[div_count.DivCount] = None,
        start_delay: typing.Optional[typing.Union[Expr, int]] = None,
        start_value: typing.Optional[typing.Union[Expr, float]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            duration=duration,
            end_value=end_value,
            interpolator=interpolator,
            items=items,
            name=name,
            repeat=repeat,
            start_delay=start_delay,
            start_value=start_value,
            **kwargs,
        )

    duration: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Animation duration in milliseconds.",
    )
    end_value: typing.Optional[typing.Union[Expr, float]] = Field(
        description="Final value of an animation.",
    )
    interpolator: typing.Optional[typing.Union[Expr, div_animation_interpolator.DivAnimationInterpolator]] = Field(
        description=(
            "Animation speed nature. When the value is set to `spring` — "
            "animation of dampingfluctuations cut to 0.7 with the "
            "`damping=1` parameter. Other options correspondto the "
            "Bezier curve:`linear` — cubic-bezier(0, 0, 1, 1);`ease` "
            "—cubic-bezier(0.25, 0.1, 0.25, 1);`ease_in` — "
            "cubic-bezier(0.42, 0, 1,1);`ease_out` — cubic-bezier(0, 0, "
            "0.58, 1);`ease_in_out` — cubic-bezier(0.42, 0,0.58, 1)."
        ),
    )
    items: typing.Optional[typing.Sequence[DivAnimation]] = Field(
        description="Animation elements.",
    )
    name: typing.Union[Expr, DivAnimationName] = Field(
        description="Animation type.",
    )
    repeat: typing.Optional[div_count.DivCount] = Field(
        description="Number of animation repetitions.",
    )
    start_delay: typing.Optional[typing.Union[Expr, int]] = Field(
        description="Delay in milliseconds before animation starts.",
    )
    start_value: typing.Optional[typing.Union[Expr, float]] = Field(
        description="Starting value of an animation.",
    )


class DivAnimationName(str, enum.Enum):
    FADE = "fade"
    TRANSLATE = "translate"
    SCALE = "scale"
    NATIVE = "native"
    SET = "set"
    NO_ANIMATION = "no_animation"


DivAnimation.update_forward_refs()
