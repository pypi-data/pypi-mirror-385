# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    div_radial_gradient_fixed_center, div_radial_gradient_relative_center,
)


DivRadialGradientCenter = Union[
    div_radial_gradient_fixed_center.DivRadialGradientFixedCenter,
    div_radial_gradient_relative_center.DivRadialGradientRelativeCenter,
]
