# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div, div_action, div_animation, div_point, div_tooltip_mode


# Tooltip.
class DivTooltip(BaseDiv):

    def __init__(
        self, *,
        animation_in: typing.Optional[div_animation.DivAnimation] = None,
        animation_out: typing.Optional[div_animation.DivAnimation] = None,
        background_accessibility_description: typing.Optional[typing.Union[Expr, str]] = None,
        close_by_tap_outside: typing.Optional[typing.Union[Expr, bool]] = None,
        div: typing.Optional[div.Div] = None,
        duration: typing.Optional[typing.Union[Expr, int]] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        mode: typing.Optional[div_tooltip_mode.DivTooltipMode] = None,
        offset: typing.Optional[div_point.DivPoint] = None,
        position: typing.Optional[typing.Union[Expr, DivTooltipPosition]] = None,
        tap_outside_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            animation_in=animation_in,
            animation_out=animation_out,
            background_accessibility_description=background_accessibility_description,
            close_by_tap_outside=close_by_tap_outside,
            div=div,
            duration=duration,
            id=id,
            mode=mode,
            offset=offset,
            position=position,
            tap_outside_actions=tap_outside_actions,
            **kwargs,
        )

    animation_in: typing.Optional[div_animation.DivAnimation] = Field(
        description=(
            "Tooltip appearance animation. By default, the tooltip will "
            "be appearing graduallywith an offset from the anchor point "
            "by 10 dp."
        ),
    )
    animation_out: typing.Optional[div_animation.DivAnimation] = Field(
        description=(
            "Tooltip disappearance animation. By default, the tooltip "
            "will disappear graduallywith an offset from the anchor "
            "point by 10 dp."
        ),
    )
    background_accessibility_description: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Description for accessibility of the tap action on the "
            "background of the tooltip."
        ),
    )
    close_by_tap_outside: typing.Optional[typing.Union[Expr, bool]] = Field(
        description="Allows dismissing tooltip by tapping outside of it.",
    )
    div: div.Div = Field(
        description=(
            "An element that will be shown in a tooltip. If there are "
            "tooltips inside anelement, they won\'t be shown."
        ),
    )
    duration: typing.Optional[typing.Union[Expr, int]] = Field(
        description=(
            "Duration of the tooltip visibility in milliseconds. When "
            "the value is set to `0`,the tooltip will be visible until "
            "the user hides it."
        ),
    )
    id: typing.Union[Expr, str] = Field(
        description=(
            "Tooltip ID. It is used to avoid re-showing. It must be "
            "unique for all elementtooltips."
        ),
    )
    mode: typing.Optional[div_tooltip_mode.DivTooltipMode] = Field(
        description="Tooltip modes.",
    )
    offset: typing.Optional[div_point.DivPoint] = Field(
        description="Shift relative to an anchor point.",
    )
    position: typing.Union[Expr, DivTooltipPosition] = Field(
        description=(
            "The position of a tooltip relative to an element it belongs "
            "to."
        ),
    )
    tap_outside_actions: typing.Optional[typing.Sequence[div_action.DivAction]] = Field(
        description=(
            "Specifies actions triggered by tapping outside the tooltip."
        ),
    )


class DivTooltipPosition(str, enum.Enum):
    LEFT = "left"
    TOP_LEFT = "top-left"
    TOP = "top"
    TOP_RIGHT = "top-right"
    RIGHT = "right"
    BOTTOM_RIGHT = "bottom-right"
    BOTTOM = "bottom"
    BOTTOM_LEFT = "bottom-left"
    CENTER = "center"


DivTooltip.update_forward_refs()
