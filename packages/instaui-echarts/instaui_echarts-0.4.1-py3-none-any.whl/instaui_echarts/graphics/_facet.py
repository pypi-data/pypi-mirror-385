from typing import Optional
from instaui_echarts.systems.dict_systems import drop_none_entries


def facet(
    *,
    row: Optional[str] = None,
    col: Optional[str] = None,
):
    return drop_none_entries({"row": row, "column": col})
