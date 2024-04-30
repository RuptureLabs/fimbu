from typing import TypeVar, Protocol
from fimbu.db import Model

T = TypeVar("T")
ModelT = TypeVar("ModelT", bound="Model")
