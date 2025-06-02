"""Utilities for parsing Japanese numeric ranges."""

from typing import Union

import pandas as pd

from .interval import Interval
from .parser import parse_jp_range


def parse(text: str) -> Interval | None:
    """Alias for :func:`parse_jp_range`."""

    return parse_jp_range(text)


def parse_series(
    obj: Union[pd.Series, pd.DataFrame]
) -> Union[pd.Series, pd.DataFrame]:
    """Parse a ``Series`` or ``DataFrame`` of textual ranges.

    Each element is parsed using :func:`parse_jp_range` and replaced
    with a :class:`pandas.Interval` instance or ``None`` when parsing fails.
    Non-string values are left as is.
    """

    def _convert(val: object):
        if isinstance(val, str):
            r = parse_jp_range(val)
            return r.to_pd_interval() if r is not None else None
        return val

    if isinstance(obj, pd.Series):
        return obj.apply(_convert)
    if isinstance(obj, pd.DataFrame):
        return obj.applymap(_convert)
    raise TypeError("parse_series expects a pandas Series or DataFrame")


__all__ = ["Interval", "parse_jp_range", "parse", "parse_series"]
