"""Utilities for parsing Japanese numeric ranges."""

from typing import Union, Sequence

import pandas as pd

from .interval import Interval
from .parser import parse_jp_range


def parse(text: str) -> Interval | None:
    """Alias for :func:`parse_jp_range`."""

    return parse_jp_range(text)


def apply_parse(
    obj: Union[pd.Series, pd.DataFrame],
    columns: Sequence[str] | None = None,
    *,
    split_numeric: bool = False,
) -> Union[pd.Series, pd.DataFrame]:
    """Parse a ``Series`` or ``DataFrame`` of textual ranges.

    Each element is parsed using :func:`parse_jp_range` and replaced
    with a :class:`pandas.Interval` instance or ``None`` when parsing fails.
    Non-string values are left as is.
    When ``obj`` is a ``DataFrame``, a subset of ``columns`` can be specified
    to apply the conversion. If not provided, all columns are converted.
    When ``split_numeric`` is ``True`` and ``obj`` is a ``DataFrame``,
    the specified columns are replaced by ``<column>_max`` and ``<column>_min``
    numeric columns holding the upper and lower bounds.
    """

    def _convert(val: object):
        if isinstance(val, str):
            r = parse_jp_range(val)
            if r is not None:
                return r if split_numeric else r.to_pd_interval()
            return None
        return val

    if isinstance(obj, pd.Series):
        converted = obj.apply(_convert)
        if not split_numeric:
            return converted
        name = obj.name or "range"
        return pd.DataFrame(
            {
                f"{name}_max": converted.map(
                    lambda v: v.upper if isinstance(v, Interval) else None
                ),
                f"{name}_min": converted.map(
                    lambda v: v.lower if isinstance(v, Interval) else None
                ),
            }
        )
    if isinstance(obj, pd.DataFrame):
        result = obj.copy()
        cols = obj.columns if columns is None else columns
        for c in cols:
            converted = result[c].apply(_convert)
            if split_numeric:
                result[f"{c}_max"] = converted.map(
                    lambda v: v.upper if isinstance(v, Interval) else None
                )
                result[f"{c}_min"] = converted.map(
                    lambda v: v.lower if isinstance(v, Interval) else None
                )
                result.drop(columns=[c], inplace=True)
            else:
                result[c] = converted
        return result
    raise TypeError("apply_parse expects a pandas Series or DataFrame")


def detect_interval_columns(df: pd.DataFrame, threshold: float = 0.5) -> pd.Index:
    """Return DataFrame columns that can be converted to :class:`Interval`.

    Parameters
    ----------
    df:
        Target DataFrame.
    threshold:
        Minimum ratio of successfully parsed non-empty values required for a
        column to be considered convertible.
    """

    def _is_empty(x: object) -> bool:
        return pd.isna(x) or (isinstance(x, str) and x.strip() == "")

    convertible: list[str] = []
    for col in df.columns:
        s = df[col]
        non_empty = s[~s.map(_is_empty)]
        if len(non_empty) == 0:
            continue
        success_ratio = non_empty.apply(
            lambda v: parse_jp_range(v).has_range() if v and isinstance(v, str) else False
        ).mean()
        if success_ratio > threshold:
            convertible.append(col)

    return pd.Index(convertible)


__all__ = [
    "Interval",
    "parse_jp_range",
    "parse",
    "apply_parse",
    "detect_interval_columns",
]
