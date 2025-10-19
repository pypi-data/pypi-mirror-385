"""Data loading utilities for the time series cleaning package.

The functions defined here are thin wrappers around pandas functions
that provide a consistent interface for reading raw data from disk.
They handle common formats such as CSV and Excel spreadsheets and
ensure that column names are normalised (e.g. spaces replaced with
underscores) so downstream functions do not need to worry about
unexpected whitespace.
"""

from typing import Optional
import pandas as pd


def load_data(path: str, *, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Load data from a file path into a DataFrame.

    Parameters
    ----------
    path : str
        The path to the file. CSV and Excel formats are supported. For
        Excel files you may provide a sheet name via ``sheet_name``.
    sheet_name : Optional[str], default None
        The name of the sheet within an Excel workbook to read. Only
        relevant when reading ``.xls`` or ``.xlsx`` files.

    Returns
    -------
    pandas.DataFrame
        The loaded data with normalised column names.

    Examples
    --------
    >>> df = load_data("reports.xlsx", sheet_name="Income Reports")
    >>> df.head()
    """
    # Determine file extension to choose the appropriate pandas reader
    lower = path.lower()
    if lower.endswith(".csv"):
        df = pd.read_csv(path)
    elif lower.endswith( (".xls", ".xlsx") ):
        # Only pass sheet_name if provided to avoid pandas defaulting
        # to the first sheet on its own (which raises a warning if None)
        if sheet_name is not None:
            df = pd.read_excel(path, sheet_name=sheet_name)
        else:
            df = pd.read_excel(path)
    else:
        raise ValueError(
            f"Unsupported file type for '{path}'. Supported formats are .csv and .xlsx"
        )

    # Normalise column names: strip whitespace, lower case, replace spaces
    df.columns = [str(c).strip().replace(" ", "_").lower() for c in df.columns]
    return df