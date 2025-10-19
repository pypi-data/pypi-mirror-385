"""Merge sequence data with demographic attributes.

When building forecasting models it is often useful to include static
attributes (e.g. age, gender, location) alongside the historical time
series values. The helper in this module joins such demographics with
the output of :func:`timeseries_cleaner.cleaner.preprocess_data` on the
identifier column.
"""

from __future__ import annotations

import pandas as pd


def merge_demographics(
    sequences: pd.DataFrame, demographics: pd.DataFrame, *, id_col: str
) -> pd.DataFrame:
    """Merge sliding window sequences with demographic data.

    Parameters
    ----------
    sequences : pandas.DataFrame
        Wide format DataFrame returned by ``preprocess_data``. Must
        contain a column named ``id_col``.
    demographics : pandas.DataFrame
        DataFrame containing one row per entity with static attributes.
        Must contain a column named ``id_col``.
    id_col : str
        Name of the identifier column shared between the two tables.

    Returns
    -------
    pandas.DataFrame
        Merged DataFrame in which the identifier column is first and
        demographic columns follow the sequence columns.
    """
    if sequences.empty:
        return pd.DataFrame()
    # Create copies to avoid mutating the originals
    seq = sequences.copy()
    demo = demographics.copy()
    # Attempt to convert id columns to numeric for robust matching
    seq[id_col] = pd.to_numeric(seq[id_col], errors="coerce")
    demo[id_col] = pd.to_numeric(demo[id_col], errors="coerce")
    # Drop rows with missing identifiers
    seq = seq.dropna(subset=[id_col])
    demo = demo.dropna(subset=[id_col])
    # Cast to int for join key if appropriate
    try:
        seq[id_col] = seq[id_col].astype(int)
        demo[id_col] = demo[id_col].astype(int)
    except Exception:
        # Fallback: leave as float if casting fails
        pass
    # Remove duplicate demo rows
    demo = demo.drop_duplicates(subset=[id_col])
    # Perform left join to retain all sequence rows even if no demographics
    merged = seq.merge(demo, on=id_col, how="left")
    # Move id column to first position
    cols = [id_col] + [c for c in merged.columns if c != id_col]
    return merged[cols]