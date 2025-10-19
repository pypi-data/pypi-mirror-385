"""Top level package for the time series cleaning library.

This package exposes a small set of utilities to clean and structure
transactional or diary style data into a form suitable for building
time‑series forecasting models. The aim is to hide the repetitive
preprocessing steps – such as converting dates to weekly buckets,
filling missing periods and creating sliding windows of features –
behind a simple and stable API that can be extended over time.

The key public functions are:

* :func:`load_data` – read raw data from common file formats (CSV and Excel)
  into a Pandas DataFrame.
* :func:`preprocess_data` – aggregate records by week and build sequences of
  past values to use as features and the subsequent value as the label.
* :func:`merge_demographics` – merge the generated sequences with
  demographic information for each entity.
* :func:`train_test_split` – split your data into train/test windows based
  on the most recent weeks of observations.

These helpers can be composed to build a complete preprocessing pipeline
for a dataset such as the provided income report diary.
"""

from .loader import load_data  # noqa: F401
from .cleaner import preprocess_data, PreprocessConfig  # noqa: F401
from .merger import merge_demographics  # noqa: F401
from .splitter import train_test_split  # noqa: F401

__all__ = [
    "load_data",
    "preprocess_data",
    "PreprocessConfig",
    "merge_demographics",
    "train_test_split",
]