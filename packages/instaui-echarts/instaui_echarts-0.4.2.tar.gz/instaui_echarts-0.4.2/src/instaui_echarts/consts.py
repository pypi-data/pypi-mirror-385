from pathlib import Path
from typing import Final


STATIC_DIR: Final = Path(__file__).parent / "static"
ECHARTS_JS_FILE: Final = STATIC_DIR / "echarts.esm.min.js"
ECHARTS_JS_CDN: Final = (
    "https://cdn.jsdelivr.net/npm/echarts@6.0.0/dist/echarts.esm.min.js"
)
