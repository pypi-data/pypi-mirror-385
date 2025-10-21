from typing import cast
from instaui.common.binding_track_mixin import is_binding_tracker
from instaui.common.var_track_mixin import mark_as_used
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.vue_computed import VueComputed


def str_format(template: str, *args, **kwargs):
    bindings = {}
    tran_args = []

    mark_as_used(args)
    mark_as_used(kwargs)

    for idx, arg in enumerate(args):
        is_mixin = is_binding_tracker(arg)
        value = (
            cast(StrFormatBindingMixin, arg)._to_str_format_binding(idx)
            if is_mixin
            else arg
        )
        tran_args.append(value[-1] if is_mixin else value)
        if is_mixin:
            bindings[value[0]] = arg

    tran_kwargs = {}

    for idx, (k, v) in enumerate(kwargs.items()):
        is_mixin = is_binding_tracker(v)
        value = (
            cast(StrFormatBindingMixin, v)._to_str_format_binding(idx)
            if is_mixin
            else v
        )
        tran_kwargs[k] = value[-1] if is_mixin else value
        if is_mixin:
            bindings[value[0]] = v

    code = "()=>`" + template.format(*tran_args, **tran_kwargs) + "`"
    return VueComputed(code, bindings=bindings)
