from __future__ import annotations

from pathlib import Path

import polars as pl
from polars.plugins import (
    register_plugin_function,  # pyright: ignore[reportUnknownVariableType]
)

_LIB = Path(__file__).parent
_ARGS = pl.first()

_ARGS_SINGLE = pl.lit(None, dtype=pl.Null)

# Utils


def is_uuid(expr: str | pl.Expr) -> pl.Expr:
    """
    Check if values in a column or expression are valid UUID strings.

    Parameters
    ----------
    expr : str or pl.Expr
        The name of the column (as a string) or a polars expression to check for valid UUID strings.

    Returns
    -------
    pl.Expr
        A boolean polars expression indicating which values are valid UUID strings.

    Examples
    --------
    >>> df = pl.DataFrame({"id": ["550e8400-e29b-41d4-a716-446655440000", "not-a-uuid"]})
    >>> df.with_columns(is_uuid("id").alias("is_valid_uuid"))
    shape: (2, 2)
    ┌──────────────────────────────────────┬───────────────┐
    │ id                                   ┆ is_valid_uuid │
    │ ---                                  ┆ ---           │
    │ str                                  ┆ bool          │
    ╞══════════════════════════════════════╪═══════════════╡
    │ 550e8400-e29b-41d4-a716-446655440000 ┆ true          │
    │ not-a-uuid                           ┆ false         │
    └──────────────────────────────────────┴───────────────┘
    """
    if isinstance(expr, str):
        expr = pl.col(expr)

    return register_plugin_function(
        args=expr,
        plugin_path=_LIB,
        function_name="is_uuid",
        is_elementwise=True,
    )


def u64_pair_to_uuid(*, high_bits: str | pl.Expr, low_bits: str | pl.Expr) -> pl.Expr:
    """
    Converts two 64-bit integer into UUID strings.

    Parameters:
        high_bits (str | pl.Expr): The column name or polars expression representing the high 64 bits of the UUID.
        low_bits (str | pl.Expr): The column name or polars expression representing the low 64 bits of the UUID.

    Returns:
        pl.Expr: A polars expression that produces a Series of UUID strings.

    Notes:
        - Both `high_bits` and `low_bits` must refer to columns or expressions of equal length.
    """
    if isinstance(high_bits, str):
        high_bits = pl.col(high_bits)

    if isinstance(low_bits, str):
        low_bits = pl.col(low_bits)

    return register_plugin_function(
        args=(high_bits, low_bits),
        plugin_path=_LIB,
        function_name="u64_pair_to_uuid_string",
        is_elementwise=True,
    )


# UUIDv4


def uuid_v4(*, scalar: bool = False) -> pl.Expr:
    """
    Generates a series of random version 4 UUIDs.

    Returns:
        pl.Expr: A polars expression of random v4 UUIDs.

    Example:
        >>> df.with_columns(uuid=uuid_v4())
    """
    if scalar:
        args = _ARGS_SINGLE
        fn_name = "uuid4_rand_single"
    else:
        args = _ARGS
        fn_name = "uuid4_rand"

    return register_plugin_function(
        args=args,
        plugin_path=_LIB,
        function_name=fn_name,
        is_elementwise=not scalar,
        returns_scalar=scalar,
    )


# UUIDv7


def uuid_v7_now(*, scalar: bool = False) -> pl.Expr:
    """
    Generates a series of random version 7 UUIDs based on the current system time.

    Returns:
        pl.Expr: A polars expression of random v7 UUIDs.

    Example:
        >>> df.with_columns(uuid=uuid_v7_now())
    """
    if scalar:
        args = _ARGS_SINGLE
        fn_name = "uuid7_rand_now_single"
    else:
        args = _ARGS
        fn_name = "uuid7_rand_now"

    return register_plugin_function(
        args=args,
        plugin_path=_LIB,
        function_name=fn_name,
        is_elementwise=not scalar,
        returns_scalar=scalar,
    )


def uuid_v7(*, timestamp: float, scalar: bool = False) -> pl.Expr:
    """
    Generates a series of random version 7 UUIDs based on the given timestamp.

    Parameters:
        timestamp (float): The timestamp to use when generating UUIDs in seconds since the UNIX epoch.

    Returns:
        pl.Expr: A polars expression of random v7 UUIDs based on the given timestamp.

    Example:
        >>> dt = datetime.datetime(2000, 1, 1, tz=datetime.UTC)
        >>> df.with_columns(uuid=uuid_v7(timestamp=dt.timestamp()))
    """
    if scalar:
        args = _ARGS_SINGLE
        fn_name = "uuid7_rand_single"
    else:
        args = _ARGS
        fn_name = "uuid7_rand"

    return register_plugin_function(
        args=args,
        plugin_path=_LIB,
        function_name=fn_name,
        is_elementwise=not scalar,
        returns_scalar=scalar,
        kwargs={"seconds_since_unix_epoch": timestamp},
    )


def uuid_v7_extract_dt(expr: str | pl.Expr, /, *, strict: bool = True) -> pl.Expr:
    """
    Extract UTC datetimes from UUIDv7 strings.

    Parameters:
        expr (str | pl.Expr): The input column name or polars expression containing UUIDv7 strings.
        strict (bool, optional): If `True`, raises an error on invalid UUIDv7 strings. If `False`, returns null for invalid entries.

    Returns:
        pl.Expr: A polars expression yielding a Series of UTC datetimes extracted from the UUIDv7 strings.

    Notes:
        - UUIDv7 timestamps have millisecond precision

    Examples:
        >>> df.with_columns(
        >>>     dt=uuid_v7_extract_dt(pl.col("uuid"), strict=False)
        >>> )

    """
    if isinstance(expr, str):
        expr = pl.col(expr)

    return register_plugin_function(
        args=expr,
        plugin_path=_LIB,
        function_name="uuid7_extract_dt",
        is_elementwise=True,
        kwargs={"strict": strict},
    )
