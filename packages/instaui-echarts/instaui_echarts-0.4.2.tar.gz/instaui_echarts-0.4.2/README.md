# instaui-echarts

<div align="center">

English| [简体中文](./README.md)

</div>

## 📖 Introduction
instaui-echarts is a Python package for instaui, which provides a component for rendering ECharts.


## ⚙️ Installation

```bash
pip install instaui-echarts
```

## 🖥️ Usage
```python
from instaui import ui
from instaui_echarts import echarts

@ui.page("/")
def test_page():
    opts = {
        "title": {"text": "ECharts Getting Started Example"},
        "tooltip": {},
        "legend": {"data": ["sales"]},
        "xAxis": {
            "data": ["Shirts", "Cardigans", "Chiffons", "Pants", "Heels", "Socks"]
        },
        "yAxis": {},
        "series": [{"name": "sales", "type": "bar", "data": [5, 20, 36, 10, 10, 20]}],
    }

    echarts(opts)


ui.server(debug=True).run()
```

use `graphics`

```python
from instaui import ui
from instaui_echarts import echarts, graphics as gh


@ui.page()
def test():
    options = gh.option(
        gh.data(
            [
                {"x": "A", "y": 10},
                {"x": "B", "y": 20},
                {"x": "C", "y": 30},
            ]
        ),
        gh.bar_y(),
    )

    echarts(options)
```