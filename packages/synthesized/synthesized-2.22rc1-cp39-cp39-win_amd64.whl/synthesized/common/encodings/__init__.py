from typing import Dict, Type

from ..module import register
from .encoding import Encoding
from .variational import VariationalEncoding

register(name="variational", module=VariationalEncoding)

Encodings: Dict[str, Type[Encoding]] = {
    "encoding": Encoding,
    "variational": VariationalEncoding,
}

__all__ = ["Encoding", "VariationalEncoding", "Encodings"]
