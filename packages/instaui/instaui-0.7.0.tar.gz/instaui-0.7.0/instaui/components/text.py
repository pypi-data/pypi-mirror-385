from __future__ import annotations
from typing import Any, Optional, Literal, Union
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.components._responsive_type._common import (
    TMaybeResponsive,
    TLevel_1_9,
)
from instaui.components._responsive_type._typography import (
    TWeightEnum,
    TTextWrapEnum,
    TTrimEnum,
    TAlignEnum,
)


class Text(Element):
    def __init__(
        self,
        text: Optional[TMaybeRef[Any]] = None,
        *,
        as_: Optional[TMaybeRef[Literal["span", "div", "label", "p"]]] = None,
        as_child: Optional[TMaybeRef[bool]] = None,
        size: Optional[TMaybeResponsive[TLevel_1_9]] = None,
        weight: Optional[TMaybeResponsive[Union[TWeightEnum, str]]] = None,
        align: Optional[TMaybeResponsive[Union[TAlignEnum, str]]] = None,
        trim: Optional[TMaybeRef[Union[TTrimEnum, str]]] = None,
        truncate: Optional[TMaybeRef[bool]] = None,
        text_wrap: Optional[TMaybeRef[Union[TTextWrapEnum, str]]] = None,
    ):
        super().__init__("ui-text")

        self.props(
            {
                "innerText": text,
                "as": as_,
                "as_child": as_child,
                "size": size,
                "weight": weight,
                "text_align": align,
                "trim": trim,
                "truncate": truncate,
                "text_wrap": text_wrap,
            }
        )
