# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import div_blur, div_filter_rtl_mirror


DivFilter = Union[
    div_blur.DivBlur,
    div_filter_rtl_mirror.DivFilterRtlMirror,
]
