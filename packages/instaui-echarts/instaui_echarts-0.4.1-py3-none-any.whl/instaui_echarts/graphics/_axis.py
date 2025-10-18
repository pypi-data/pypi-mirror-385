from typing import Optional, Union
from instaui_echarts.mixins import XAxisMixin, YAxisMixin
from instaui_echarts.systems.dict_systems import drop_none_entries


class BaseAxis:
    def __init__(
        self, *, show: Optional[bool] = None, options: Optional[dict] = None
    ) -> None:
        self._show = show
        self._options = options

    def _to_base_config(self) -> Union[list[dict], dict]:
        return drop_none_entries({"show": self._show, **(self._options or {})})


class XAxis(XAxisMixin, BaseAxis):
    def __init__(
        self, *, show: Optional[bool] = None, options: Optional[dict] = None
    ) -> None:
        super().__init__(show=show, options=options)

    def to_config(self) -> Union[list[dict], dict]:
        return super()._to_base_config()


class YAxis(YAxisMixin, BaseAxis):
    def __init__(
        self, *, show: Optional[bool] = None, options: Optional[dict] = None
    ) -> None:
        super().__init__(show=show, options=options)

    def to_config(self) -> Union[list[dict], dict]:
        return super()._to_base_config()
