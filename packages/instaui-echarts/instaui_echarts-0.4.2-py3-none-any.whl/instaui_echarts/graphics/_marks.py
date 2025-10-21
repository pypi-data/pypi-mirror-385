from __future__ import annotations
from typing import Optional, Union
from instaui_echarts.mixins import MarkMixin
from instaui_echarts.systems.dict_systems import drop_none_entries
from instaui_echarts.graphics._data import DataSpec


class BarYMark(MarkMixin):
    def __init__(
        self,
        *,
        x: Optional[str] = None,
        y: Optional[str] = None,
        label: Optional[str] = None,
        tooltip: Optional[Union[str, list[str]]] = None,
        facet: Optional[dict] = None,
        series_options: Optional[dict] = None,
    ) -> None:
        self._x = x
        self._y = y
        self._label = label
        self._tooltip = tooltip
        self._facet = facet
        self._series_options = series_options

    def to_config(self) -> dict:
        return drop_none_entries(
            {
                "type": "bar",
                "x": self._x,
                "y": self._y,
                "label": self._label,
                "tooltip": self._tooltip,
                "facet": self._facet,
                "echarts": self._series_options,
            }
        )


class LineMark(MarkMixin):
    def __init__(
        self,
        *,
        x: Optional[str] = None,
        y: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        tooltip: Optional[Union[str, list[str]]] = None,
        facet: Optional[dict] = None,
        series_options: Optional[dict] = None,
    ) -> None:
        self._x = x
        self._y = y
        self._color = color
        self._label = label
        self._tooltip = tooltip
        self._facet = facet
        self._series_options = series_options

    def to_config(self) -> dict:
        return drop_none_entries(
            {
                "type": "line",
                "x": self._x,
                "y": self._y,
                "color": self._color,
                "label": self._label,
                "tooltip": self._tooltip,
                "facet": self._facet,
                "echarts": self._series_options,
            }
        )


class PieMark(MarkMixin):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        value: Optional[str] = None,
        tooltip: Optional[Union[str, list[str]]] = None,
        facet: Optional[dict] = None,
        series_options: Optional[dict] = None,
    ) -> None:
        self._name = name
        self._value = value
        self._tooltip = tooltip
        self._facet = facet
        self._series_options = series_options

    def to_config(self) -> dict:
        return drop_none_entries(
            {
                "type": "pie",
                "name": self._name,
                "value": self._value,
                "tooltip": self._tooltip,
                "facet": self._facet,
                "echarts": self._series_options,
            }
        )


class PointMark(MarkMixin):
    def __init__(
        self,
        *,
        x: Optional[str] = None,
        y: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        tooltip: Optional[Union[str, list[str]]] = None,
        facet: Optional[dict] = None,
        series_options: Optional[dict] = None,
    ) -> None:
        self._x = x
        self._y = y
        self._size = size
        self._color = color
        self._label = label
        self._tooltip = tooltip
        self._facet = facet
        self._series_options = series_options

    def to_config(self) -> dict:
        return drop_none_entries(
            {
                "type": "scatter",
                "x": self._x,
                "y": self._y,
                "size": self._size,
                "color": self._color,
                "label": self._label,
                "tooltip": self._tooltip,
                "facet": self._facet,
                "echarts": self._series_options,
            }
        )


class EffectPointMark(MarkMixin):
    def __init__(
        self,
        *,
        x: Optional[str] = None,
        y: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        tooltip: Optional[Union[str, list[str]]] = None,
        data: Optional[DataSpec] = None,
        facet: Optional[dict] = None,
        series_options: Optional[dict] = None,
    ) -> None:
        self._x = x
        self._y = y
        self._size = size
        self._color = color
        self._label = label
        self._tooltip = tooltip
        self._facet = facet
        self._series_options = series_options
        self._data = data

    def to_config(self) -> dict:
        return drop_none_entries(
            {
                "type": "effect-scatter",
                "x": self._x,
                "y": self._y,
                "size": self._size,
                "color": self._color,
                "label": self._label,
                "tooltip": self._tooltip,
                "facet": self._facet,
                "echarts": self._series_options,
                "data": self._data if self._data is None else self._data.to_config(),
            }
        )


class RuleXMark(MarkMixin):
    def __init__(
        self,
        data: Union[DataSpec, list[Union[str, int, float]]],
        *,
        x: Optional[str] = None,
        y1: Optional[str] = None,
        y2: Optional[str] = None,
        line_style: Optional[dict] = None,
    ) -> None:
        self._x = x
        self._y1 = y1
        self._y2 = y2
        self._line_style = line_style
        self._data = data

    def to_config(self) -> dict:
        base_config: dict = {
            "type": "rule",
            "rType": "x",
            "lineStyle": self._line_style,
        }

        if isinstance(self._data, DataSpec):
            base_config["map"] = {
                "x1": self._x,
                "y1": self._y1,
                "y2": self._y2,
            }
            base_config["data"] = self._data.to_config()
        else:
            base_config["value"] = {"value": self._data}

        return drop_none_entries(base_config)


class RuleYMark(MarkMixin):
    def __init__(
        self,
        data: Union[DataSpec, list[Union[str, int, float]]],
        *,
        y: Optional[str] = None,
        x1: Optional[str] = None,
        x2: Optional[str] = None,
        line_style: Optional[dict] = None,
    ) -> None:
        self._y = y
        self._x1 = x1
        self._x2 = x2
        self._line_style = line_style
        self._data = data

    def to_config(self) -> dict:
        base_config: dict = {
            "type": "rule",
            "rType": "y",
            "lineStyle": self._line_style,
        }

        if isinstance(self._data, DataSpec):
            base_config["map"] = {
                "y1": self._y,
                "x1": self._x1,
                "x2": self._x2,
            }
            base_config["data"] = self._data.to_config()
        else:
            base_config["value"] = {"value": self._data}

        return drop_none_entries(base_config)


def rule_line_style(
    *, color: Optional[str] = None, width: Optional[int] = None
) -> dict:
    return drop_none_entries({"color": color, "width": width})
