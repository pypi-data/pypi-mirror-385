from typing import Literal, Optional, Union
from instaui_echarts.mixins import ToolTipMixin
from instaui_echarts.systems.dict_systems import drop_none_entries


class ToolTip(ToolTipMixin):
    def __init__(
        self,
        *,
        trigger: Optional[Literal["item", "axis", "none"]] = None,
        options: Optional[dict] = None,
    ) -> None:
        self._trigger = trigger
        self._options = options

    def to_config(self) -> Union[list[dict], dict]:
        return drop_none_entries({"trigger": self._trigger, **(self._options or {})})
