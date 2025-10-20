import polars as pl
import logging
from polars._typing import FileSource
from typing import Any, Sequence

logger = logging.getLogger(__name__)


def read_excel(
    source: FileSource,
    *,
    sheet_id: int | None = None,
    sheet_name: str | None = None,
    header_row: int | None = 0,
    has_header: bool = True,
    columns: Sequence[int] | Sequence[str] | str | None = None,
    read_options: dict[str, Any] | None = None,
    drop_empty_rows: bool = True,
    drop_empty_cols: bool = True,
    raise_if_empty: bool = True,
    cast: dict[str, pl.DataType] | None = None,
    **kwargs: Any,
) -> pl.LazyFrame:
    """
    Read an Excel file into a Polars LazyFrame with enhanced processing options.

    This function extends Polars' read_excel functionality by adding automatic
    column name cleaning and optional data type casting. It reads Excel data and returns aLazyFrame for efficient data processing.

    Parameters
    ----------
    source : FileSource
        Path to the Excel file or file-like object to read
    sheet_id : int, optional
        Sheet number to read (cannot be used with sheet_name)
    sheet_name : str, optional
        Sheet name to read (cannot be used with sheet_id)
    header_row : int, optional
        Row index of the header row (default is 0)
    has_header : bool, default=True
        Whether the sheet has a header row
    columns : Sequence[int] | Sequence[str] | str, optional
        Columns to select (by index or name)
    read_options : dict[str, Any], optional
        Dictionary of read options passed to polars.read_excel
    drop_empty_rows : bool, default=True
        Remove empty rows from the result
    drop_empty_cols : bool, default=True
        Remove empty columns from the result
    raise_if_empty : bool, default=True
        Raise an exception if the resulting DataFrame is empty
    cast : dict[str, pl.DataType], optional
        Dictionary mapping column names to desired data types for casting.
        Note: Column names will be automatically stripped and converted to lowercase,
        so specify column names in lowercase when using this parameter.
    **kwargs : Any
        Additional keyword arguments passed to polars.read_excel

    Returns
    -------
    pl.LazyFrame
        A Polars LazyFrame containing the Excel data with cleaned column names
        and optional type casting applied

    Raises
    ------
    ValueError
        If both sheet_id and sheet_name are specified

    Examples
    --------
    >>> df = read_excel("data.xlsx")
    >>> df = read_excel("data.xlsx", sheet_name="Sheet1")
    >>> df = read_excel("data.xlsx", cast={"date": pl.Date, "value": pl.Float64})
    """
    if sheet_id is not None and sheet_name is not None:
        raise ValueError("sheet_id and sheet_name cannot be both specified.")

    if has_header:
        read_options = {
            "header_row": header_row,
        }

    df = pl.read_excel(
        source,
        sheet_id=sheet_id,
        sheet_name=sheet_name,
        read_options=read_options,
        has_header=has_header,
        columns=columns,
        drop_empty_rows=drop_empty_rows,
        drop_empty_cols=drop_empty_cols,
        raise_if_empty=raise_if_empty,
        **kwargs,
    )

    df.columns = [col.strip().lower() for col in df.columns]
    logger.info(f"Intial df rows: {df.height}, columns: {df.width}")

    if df.is_empty():
        logger.warning("Dataframe is empty.")

    if cast is not None:
        for col, dtype in cast.items():
            if col not in df.columns:
                logger.warning(f"Column {col} not found in dataframe.")
                continue

            logger.info(f"Casting column {col} to {dtype}")
            df = df.with_columns(pl.col(col).cast(dtype, strict=False))

    return df.lazy()


def find_header_row(
    source: FileSource,
    sheet_id: int | None = None,
    sheet_name: str | None = None,
    max_rows: int = 100,
    expected_keywords: list[str] | None = None,
) -> int:
    """
    Find the header row in an Excel file by identifying the first row with maximum consecutive non-null values.

    This function is designed for Excel sheets where headers are not at the top row and the rows
    above the header row contain data. It identifies the most likely header row by scanning for
    the row with the highest number of consecutive non-null string values.

    Parameters
    ----------
    source : FileSource
        Path to the Excel file or file-like object to read
    sheet_id : int, optional
        Sheet number to read (cannot be used with sheet_name)
    sheet_name : str, optional
        Sheet name to read (cannot be used with sheet_id)
    max_rows : int, default=100
        Maximum number of rows to scan for header identification
    expected_keywords : list[str], optional
        List of keywords to look for in the header row. If a row contains all of these keywords, it is considered a header row.

    Returns
    -------
    int
        The zero-based index of the first row with maximum consecutive non-null values. If expected_keywords is provided, this is the first row with all expected keywords and maximum consecutive non-null values.

    Examples
    --------
    >>> header_row_index = find_header_row("data.xlsx")
    >>> df = read_excel("data.xlsx", header_row=header_row_index)

    Notes
    -----
    - If the first few rows are empty and the header is at the top of the data section,
      use `read_excel` directly instead of this function
    - The function considers consecutive non-null values from the beginning of each row
    - Only one of `sheet_id` or `sheet_name` can be specified
    """
    if sheet_id is not None and sheet_name is not None:
        raise ValueError("sheet_id and sheet_name cannot be both specified.")

    # Read first 100 rows without assuming header row
    df = pl.read_excel(
        source,
        sheet_id=sheet_id,
        sheet_name=sheet_name,
        drop_empty_cols=False,
        drop_empty_rows=False,
        has_header=False,
    ).head(max_rows)

    max_consecutive = 0
    header_row_index = 0

    for i, row in enumerate(df.rows()):
        consecutive_count = 0
        # If expected keywords are provided, check if all of them are present in the row
        all_keywords_present = False
        if expected_keywords:
            row_values = [
                str(value).strip().lower() for value in row if value is not None
            ]
            all_keywords_present = all(
                keyword.lower() in row_values for keyword in expected_keywords
            )

        # Check for non-null consecutive values
        for value in row:
            if value is not None and str(value).strip() != "":
                consecutive_count += 1
            else:
                break

        if consecutive_count > max_consecutive:
            max_consecutive = consecutive_count
            header_row_index = i
            if expected_keywords and all_keywords_present:
                # This is the first row with all expected keywords, and highest consecutive non-null count, so its most likely the header row
                logger.info(
                    "Found first header row with all expected keywords and maximum consecutive non-null values"
                )
                break

    logger.info(
        f"Identified header row at index: {header_row_index} with {max_consecutive} consecutive non-null values"
    )
    return header_row_index
