"""Helper for splitting raw data into training and testing windows.

This module provides a convenience function to divide a dataset into
temporal train and test portions before preprocessing. It determines
the latest week present in the data and then defines the test set as
the most recent ``weeks_back + window`` weeks. The training set
excludes the last ``weeks_back`` weeks. Both splits are then
transformed into sliding window sequences via
:func:`timeseries_cleaner.cleaner.preprocess_data`.

Note that this function assumes the ``week`` identifiers follow the
same format used in :func:`timeseries_cleaner.cleaner.preprocess_data`.
"""

from __future__ import annotations

from typing import Tuple, Optional
import pandas as pd

from .cleaner import preprocess_data, PreprocessConfig
from .merger import merge_demographics


def _parse_week_string(week_str: str) -> Tuple[int, int]:
    """Parse a year-week string of the form 'YYYY-wkWW' into integers.

    Returns a tuple ``(year, week_num)``. Assumes the string ends with
    a two-digit week number.
    """
    try:
        year_part, wk_part = week_str.split("-wk")
        return int(year_part), int(wk_part)
    except Exception as exc:
        raise ValueError(f"Invalid week string format: {week_str}") from exc


def train_test_split(
    df: pd.DataFrame,
    *,
    config: PreprocessConfig,
    weeks_back: int = 3,
    demographics: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split a raw dataset into train/test partitions and preprocess each.

    Parameters
    ----------
    df : pandas.DataFrame
        Raw input data containing at least the columns defined in
        ``config``.
    config : PreprocessConfig
        Configuration specifying column names and window length.
    weeks_back : int, default 3
        Number of weeks to hold out for testing. The test set will
        include the last ``weeks_back + config.window`` weeks of data,
        ensuring that sequences in the test set have sufficient history.
    demographics : Optional[pandas.DataFrame], default None
        Optional DataFrame with demographic information to merge with
        the processed sequences.

    Returns
    -------
    train_processed : pandas.DataFrame
        Preprocessed training sequences (optionally merged with
        demographics).
    test_processed : pandas.DataFrame
        Preprocessed testing sequences (optionally merged with
        demographics).
    full_processed : pandas.DataFrame
        Preprocessed sequences for the entire dataset (optionally merged
        with demographics).
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # Copy and derive week identifiers consistently with preprocess_data
    tmp = df[[config.id_col, config.date_col, config.value_col]].copy()
    tmp[config.date_col] = pd.to_datetime(tmp[config.date_col])
    tmp["week"] = tmp[config.date_col].dt.strftime(config.week_format)

    # Determine the most recent week present in the data
    latest_week = tmp["week"].max()
    year, week_num = _parse_week_string(latest_week)

    # Build lists of week identifiers for test and exclusion
    # Test set should include the last (weeks_back + window) weeks
    test_weeks: list[str] = []
    for i in range(config.window + weeks_back):
        w = week_num - i
        y = year
        # Handle year roll‑over if week index becomes <= 0
        while w <= 0:
            y -= 1
            # Use 52 as the max number of weeks per year for %U formatting
            w += 52
        test_weeks.append(f"{y}-wk{w:02d}")
    # Remove duplicates and sort
    test_weeks = sorted(set(test_weeks))

    # Weeks reserved purely for prediction targets (weeks_back) are the
    # most recent weeks_back entries
    exclude_weeks: list[str] = []
    for i in range(weeks_back):
        w = week_num - i
        y = year
        while w <= 0:
            y -= 1
            w += 52
        exclude_weeks.append(f"{y}-wk{w:02d}")
    exclude_weeks = sorted(set(exclude_weeks))

    # Partition the raw data
    train_df = tmp[~tmp["week"].isin(exclude_weeks)]
    test_df = tmp[tmp["week"].isin(test_weeks)]

    # Preprocess the splits separately
    train_processed = preprocess_data(train_df, config=config)
    test_processed = preprocess_data(test_df, config=config)
    full_processed = preprocess_data(tmp, config=config)

    # Optionally merge demographics
    if demographics is not None:
        train_processed = merge_demographics(train_processed, demographics, id_col=config.id_col)
        test_processed = merge_demographics(test_processed, demographics, id_col=config.id_col)
        full_processed = merge_demographics(full_processed, demographics, id_col=config.id_col)

    return train_processed, test_processed, full_processed