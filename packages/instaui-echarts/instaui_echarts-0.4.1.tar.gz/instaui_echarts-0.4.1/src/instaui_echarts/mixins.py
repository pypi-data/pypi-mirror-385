from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Union


class SpecMixin(ABC):
    @abstractmethod
    def to_option(self):
        pass


class MarkMixin(ABC):
    @abstractmethod
    def to_config(self) -> dict:
        pass


class DataMixin(ABC):
    @abstractmethod
    def to_config(self) -> Union[list[dict], dict]:
        pass


class XAxisMixin(ABC):
    @abstractmethod
    def to_config(self) -> Union[list[dict], dict]:
        pass


class YAxisMixin(ABC):
    @abstractmethod
    def to_config(self) -> Union[list[dict], dict]:
        pass


class ToolTipMixin(ABC):
    @abstractmethod
    def to_config(self) -> Union[list[dict], dict]:
        pass
