"""Core cleaning and sequence construction functions.

This module implements the heavy lifting for preparing raw transactional
or diary data for time series modelling. The primary entrypoint is
``preprocess_data`` which takes a long‑format table of observations
indexed by entity, date and value and returns a wide‑format table
with fixed length sliding windows of past values and a next step target.

The algorithm mirrors the approach used in the provided ``Analysis``
class but generalises it so it can be reused across different datasets
with varying column names. Missing weeks are automatically filled with
zero and the length of the look‑back window can be configured.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import pandas as pd


@dataclass
class PreprocessConfig:
    """Configuration for the preprocessing pipeline.

    Attributes
    ----------
    date_col : str
        Name of the column containing dates (as strings or datetime64).
    value_col : str
        Name of the column containing the numerical value to aggregate.
    id_col : str
        Name of the column identifying the entity (e.g. respondent id).
    window : int, default 6
        The number of past periods to include as features. The target
        period immediately follows the window.
    min_year : Optional[int]
        The earliest calendar year to consider when filling missing
        periods. If omitted the minimum year present in ``date_col`` is used.
    max_year : Optional[int]
        The latest calendar year to consider when filling missing
        periods. If omitted the maximum year present in ``date_col`` is used.
    week_format : str, default "%Y-wk%U"
        The strftime pattern used to derive the week identifier. By
        default it uses ``%U`` which counts weeks starting on Sunday
        with values from 00–53. You can customise this to e.g. ``%G‑wk%V``
        to use ISO weeks.
    """

    date_col: str
    value_col: str
    id_col: str
    window: int = 6
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    week_format: str = "%Y-wk%U"


def _generate_week_index(min_year: int, max_year: int) -> List[str]:
    """Generate a complete list of week identifiers between two years.

    Returns a list of strings like ``["2021-wk01", "2021-wk02", …]``
    for all weeks from January of ``min_year`` through December of
    ``max_year``. Weeks are numbered with two digits.
    """
    weeks: List[str] = []
    for year in range(min_year, max_year + 1):
        # Weeks range from 1–52 inclusive for %U. Some years may have a 53rd week
        for week_num in range(1, 54):
            weeks.append(f"{year}-wk{week_num:02d}")
    return weeks


def preprocess_data(
    df: pd.DataFrame,
    *,
    config: PreprocessConfig,
) -> pd.DataFrame:
    """Aggregate and restructure a raw event table into fixed length sequences.

    The function expects a DataFrame containing at least an identifier
    column, a date column and a numeric value column. It will:

    1. Convert the date column into weekly buckets using the specified
       format.
    2. Aggregate the value by entity and week (summing multiple events
       falling in the same week).
    3. Create a complete weekly timeline per entity, filling missing
       weeks with zeros between the provided ``min_year`` and ``max_year``.
    4. Slide a window of length ``window + 1`` over the timeline and
       produce a row for each position. The last element of the window
       becomes the target (label) and the preceding elements become
       features ``lag1``, ``lag2``, …, ``lag{window}``.
    5. Drop windows where the target is missing (NaN) and where the
       entire window sums to zero to remove uninformative periods.

    Parameters
    ----------
    df : pandas.DataFrame
        The raw data to preprocess.
    config : PreprocessConfig
        A configuration object specifying column names, window length
        and optional year bounds.

    Returns
    -------
    pandas.DataFrame
        A wide format DataFrame with one row per sliding window per
        entity. Columns are named ``lag1`` … ``lag{window}``, ``target``
        and the identifier column.
    """
    if df.empty:
        return pd.DataFrame()

    # Copy to avoid modifying original data
    data = df[[config.id_col, config.date_col, config.value_col]].copy()
    # Convert date column to datetime
    data[config.date_col] = pd.to_datetime(data[config.date_col])
    # Derive week identifier
    data["week"] = data[config.date_col].dt.strftime(config.week_format)

    # Determine year bounds if not provided
    min_year = config.min_year if config.min_year is not None else data[config.date_col].dt.year.min()
    max_year = config.max_year if config.max_year is not None else data[config.date_col].dt.year.max()

    # Prepare final result container
    feature_cols = [f"lag{i+1}" for i in range(config.window)] + ["target"]
    final = pd.DataFrame(columns=feature_cols + [config.id_col])

    # Precompute the full list of weeks to speed up missing week filling
    week_index = _generate_week_index(min_year, max_year)
    week_set = set(week_index)

    # Process each entity separately
    unique_ids = data[config.id_col].dropna().unique()
    for entity_id in unique_ids:
        subset = data[data[config.id_col] == entity_id]
        if subset.empty:
            continue
        # Aggregate by week
        weekly = (
            subset.groupby("week")[config.value_col]
            .sum()
            .reindex(week_index, fill_value=0)
            .reset_index()
            .rename(columns={"week": "week", config.value_col: "value"})
        )
        # Sort by the week index order
        # Already sorted because week_index is sorted
        values = weekly["value"].tolist()
        total_len = len(values)
        # Slide a window of length window+1
        for start_idx in range(total_len - (config.window + 1) + 1):
            window_values = values[start_idx : start_idx + config.window + 1]
            # Skip if the last element (target) is missing
            target_value = window_values[-1]
            if pd.isna(target_value):
                continue
            # Skip windows where all values sum to zero (uninformative)
            if sum(window_values) == 0:
                continue
            row = {f"lag{i+1}": window_values[i] for i in range(config.window)}
            row["target"] = target_value
            row[config.id_col] = entity_id
            final = pd.concat([final, pd.DataFrame([row])], ignore_index=True)

    # Cast numeric columns to float to ensure consistent types
    numeric_cols = [c for c in feature_cols]
    final[numeric_cols] = final[numeric_cols].astype(float)
    # Ensure id column type matches input type (often int or string)
    return final.reset_index(drop=True)