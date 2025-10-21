from typing import Optional
from instaui.zero.options import CdnResourceOption
from instaui_echarts import consts


def override(
    *,
    echarts_js: Optional[str] = None,
) -> CdnResourceOption:
    if echarts_js is None:
        return default_override()

    return CdnResourceOption(import_maps={"echarts": echarts_js})


def default_override() -> CdnResourceOption:
    return override(
        echarts_js=consts.ECHARTS_JS_CDN,
    )
