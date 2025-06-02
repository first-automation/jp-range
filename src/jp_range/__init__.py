"""Utilities for parsing Japanese numeric ranges."""

from typing import Union

import pandas as pd

from .interval import Interval
from .parser import parse_jp_range


def parse(text: str) -> Interval:
    """Alias for :func:`parse_jp_range`."""

    return parse_jp_range(text)


def parse_series(
    obj: Union[pd.Series, pd.DataFrame]
) -> Union[pd.Series, pd.DataFrame]:
    """Parse a ``Series`` or ``DataFrame`` of textual ranges.

    Each element is parsed using :func:`parse_jp_range` and replaced
    with an :class:`Interval` instance. Non-string values are left as is.
    """

    if isinstance(obj, pd.Series):
        return obj.apply(
            lambda x: parse_jp_range(x) if isinstance(x, str) else x
        )
    if isinstance(obj, pd.DataFrame):
        return obj.applymap(
            lambda x: parse_jp_range(x) if isinstance(x, str) else x
        )
    raise TypeError("parse_series expects a pandas Series or DataFrame")


__all__ = ["Interval", "parse_jp_range", "parse", "parse_series"]
