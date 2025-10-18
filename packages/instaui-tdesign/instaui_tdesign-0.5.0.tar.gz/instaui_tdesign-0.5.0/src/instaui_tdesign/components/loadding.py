from __future__ import annotations
import typing
from ._base_element import BaseElement
from typing_extensions import TypedDict, Unpack
from ._utils import handle_props

if typing.TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Loading(BaseElement):
    def __init__(
        self,
        indicator: typing.Optional[bool] = None,
        *,
        text: typing.Optional[typing.Any] = None,
        **kwargs: Unpack[TLoadingProps],
    ):
        super().__init__("t-loading")
        self.props({"text": text, "indicator": indicator})
        self.props(handle_props(kwargs))  # type: ignore


class TLoadingProps(TypedDict, total=False):
    attach: TMaybeRef[str]
    content: TMaybeRef[str]
    delay: TMaybeRef[float]
    fullscreen: TMaybeRef[bool]
    inherit_color: TMaybeRef[bool]
    loading: TMaybeRef[bool]
    prevent_scroll_through: TMaybeRef[bool]
    show_overlay: TMaybeRef[bool]
    size: TMaybeRef[str]
    z_index: TMaybeRef[float]
