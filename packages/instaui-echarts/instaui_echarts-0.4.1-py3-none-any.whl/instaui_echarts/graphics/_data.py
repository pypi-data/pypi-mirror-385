from typing import Union, Protocol, Iterable, runtime_checkable
from instaui_echarts.mixins import DataMixin


# region pandas protocol


@runtime_checkable
class PandasDataFrameValuesProtocol(Protocol):
    def tolist(self) -> list: ...


@runtime_checkable
class PandasDataFrameProtocol(Protocol):
    @property
    def columns(self) -> Iterable[str]: ...

    @property
    def values(self) -> PandasDataFrameValuesProtocol: ...


# endregion


# region polars protocol


@runtime_checkable
class PolarsDataFrameProtocol(Protocol):
    @property
    def columns(self) -> list[str]: ...

    def rows(self) -> list: ...


# endregion


class DataSpec(DataMixin):
    def __init__(
        self,
        source: Union[
            list[dict], dict, PandasDataFrameProtocol, PolarsDataFrameProtocol
        ],
    ):
        if isinstance(source, PandasDataFrameProtocol):
            self._source = _pandas_to_source(source)

        elif isinstance(source, PolarsDataFrameProtocol):
            self._source = _polars_to_source(source)
        else:
            self._source = source

    @classmethod
    def with_dimensions(cls, data: list[list], dimensions: list[str]):
        return cls({"dimensions": dimensions, "source": data})

    @classmethod
    def from_pandas(cls, dataframe: PandasDataFrameProtocol):
        return cls(_pandas_to_source(dataframe))

    @classmethod
    def from_polars(cls, dataframe: PolarsDataFrameProtocol):
        return cls(_polars_to_source(dataframe))

    def to_config(self) -> Union[list[dict], dict]:
        return self._source


def _pandas_to_source(dataframe: PandasDataFrameProtocol) -> dict:
    return {"dimensions": list(dataframe.columns), "source": dataframe.values.tolist()}


def _polars_to_source(dataframe: PolarsDataFrameProtocol) -> dict:
    return {"dimensions": dataframe.columns, "source": dataframe.rows()}
