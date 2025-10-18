import typing
from instaui.common.binding_track_mixin import (
    BindingTrackerMixin,
    try_mark_binding,
    is_binding_tracker,
)
from instaui.common.var_track_mixin import VarTrackerMixin, mark_as_used
from instaui.runtime.scope import Scope
from instaui.vars._types import InputBindingType
from instaui.vars.mixin_types.py_binding import CanInputMixin


class InputSilentData(CanInputMixin, BindingTrackerMixin, VarTrackerMixin):
    def __init__(self, value: typing.Union[BindingTrackerMixin, typing.Any]) -> None:
        self.value = value

    def is_const_value(self) -> bool:
        return not is_binding_tracker(self.value)

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _mark_binding(self, scope: Scope) -> dict:
        return try_mark_binding(self.value, scope=scope)

    def _mark_as_used(self):
        mark_as_used(self.value)
