try:
    from .version import __version__
except ModuleNotFoundError:
    from importlib_metadata import version as _version

    __version__ = _version("synthesized")
import os
import warnings

if os.environ.get("SYNTHESIZED_TP_WARNINGS", "false").lower() != "true":
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
    import tensorflow as tf

    tf.get_logger().setLevel("ERROR")
    tf.autograph.set_verbosity(0)
    for module in ["numpy", "pandas", "sklearn", "tensorflow"]:
        warnings.filterwarnings("ignore", module=module, append=True)
    warnings.filterwarnings("ignore", category=FutureWarning)

import pandas as pd

import synthesized._licence as _licence

from .common.synthesizer import Synthesizer
from .complex.conditional import ConditionalSampler
from .complex.data_imputer import DataImputer
from .complex.event_synthesizer import EventSynthesizer
from .complex.highdim import HighDimSynthesizer
from .complex.multi_table import ForeignKey, MultiTableSynthesizer
from .complex.time_series_synthesizer import TimeSeriesSynthesizer
from .complex.two_table import TwoTableDeepSynthesizer
from .complex.two_table_shallow import TwoTableSynthesizer
from .metadata.data_frame_meta import DataFrameMeta
from .metadata.factory import MetaExtractor

pd.options.mode.use_inf_as_na = True


__all__ = [
    "__version__",
    "HighDimSynthesizer",
    "ConditionalSampler",
    "DataImputer",
    "Synthesizer",
    "DataFrameMeta",
    "MetaExtractor",
    "TimeSeriesSynthesizer",
    "EventSynthesizer",
    "MultiTableSynthesizer",
    "ForeignKey",
    "TwoTableSynthesizer",
    "TwoTableDeepSynthesizer",
    "_licence",
]
