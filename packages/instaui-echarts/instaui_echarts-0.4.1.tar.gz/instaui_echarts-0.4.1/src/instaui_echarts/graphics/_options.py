from typing import Optional, Union
from instaui import custom
from instaui.common.binding_track_mixin import BindingTrackerMixin
from instaui_echarts.mixins import (
    SpecMixin,
    MarkMixin,
    DataMixin,
    XAxisMixin,
    YAxisMixin,
    ToolTipMixin,
)
from instaui_echarts.systems.dict_systems import drop_none_entries


class SpecOption(SpecMixin):
    def __init__(
        self,
        *,
        marks: list[MarkMixin],
        data: Optional[DataMixin] = None,
        echarts_options: Optional[dict] = None,
    ):
        self._marks = marks
        self._data = data
        self._echarts_options = echarts_options

    def to_option(self):
        marks = [mark.to_config() for mark in self._marks]
        grammar: dict = {"marks": marks}
        result_dict: dict = {"grammar": grammar}

        if self._data:
            grammar["data"] = self._data.to_config()
        if self._echarts_options:
            grammar["echartsOptions"] = self._echarts_options

        ref_info = self.__extract_ref_info(grammar)
        if ref_info:
            grammar, ref_info_list = ref_info

            if ref_info_list:
                result_dict["refSets"] = ref_info_list

        return result_dict

    def __extract_ref_info(self, config: dict) -> Union[None, tuple[dict, list[dict]]]:
        if not config:
            return None

        new_config = config
        refs_info = []

        # stack element structure: (current dict or list, current path)
        stack: list[tuple[Union[dict, list], list[Union[str, int]]]] = [
            (new_config, [])
        ]

        while stack:
            current, path = stack.pop()

            if isinstance(current, dict):
                for k, v in current.items():
                    if isinstance(v, BindingTrackerMixin):
                        refs_info.append(
                            {
                                "path": path + [k],
                                "ref": custom.convert_reference(v),
                            }
                        )
                        # replace Ref with None
                        current[k] = None
                    elif isinstance(v, (dict, list)):
                        stack.append((v, path + [k]))
                    # skip other types
            elif isinstance(current, list):
                for i, v in enumerate(current):
                    if isinstance(v, BindingTrackerMixin):
                        refs_info.append(
                            {
                                "path": path + [i],
                                "ref": custom.convert_reference(v),
                            }
                        )
                        current[i] = None
                    elif isinstance(v, (dict, list)):
                        stack.append((v, path + [i]))
                    # skip other types

        return new_config, refs_info


def option(*args, echarts_options: Optional[dict] = None):
    marks: list[MarkMixin] = []
    data: list[DataMixin] = []
    x_axis: list[XAxisMixin] = []
    y_axis: list[YAxisMixin] = []
    tooltip: list[ToolTipMixin] = []

    for arg in args:
        if isinstance(arg, MarkMixin):
            marks.append(arg)

        if isinstance(arg, DataMixin):
            data.append(arg)

        if isinstance(arg, XAxisMixin):
            x_axis.append(arg)

        if isinstance(arg, YAxisMixin):
            y_axis.append(arg)

        if isinstance(arg, ToolTipMixin):
            tooltip.append(arg)

    if data and len(data) > 1:
        raise ValueError("Only one data source is allowed")

    base_options = drop_none_entries(
        {
            "xAxis": x_axis[0].to_config() if x_axis else None,
            "yAxis": y_axis[0].to_config() if y_axis else None,
            "tooltip": tooltip[0].to_config() if tooltip else None,
        }
    )

    return SpecOption(
        marks=marks,
        data=data[0] if data else None,
        echarts_options={**base_options, **(echarts_options or {})},
    )
