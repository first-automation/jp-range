from __future__ import annotations

from typing import Optional
import re

from pydantic import BaseModel


class Interval(BaseModel):
    """Represents a numeric interval."""

    lower: Optional[float] = None
    upper: Optional[float] = None
    lower_inclusive: bool = False
    upper_inclusive: bool = False

    def __str__(self) -> str:
        lower_bracket = "[" if self.lower_inclusive else "("
        upper_bracket = "]" if self.upper_inclusive else ")"
        lower_val = str(self.lower) if self.lower is not None else "-inf"
        upper_val = str(self.upper) if self.upper is not None else "inf"
        return f"{lower_bracket}{lower_val}, {upper_val}{upper_bracket}"

    def contains(self, value: float) -> bool:
        """Return True if the value is inside this interval."""
        if self.lower is not None:
            if self.lower_inclusive:
                if value < self.lower:
                    return False
            else:
                if value <= self.lower:
                    return False
        if self.upper is not None:
            if self.upper_inclusive:
                if value > self.upper:
                    return False
            else:
                if value >= self.upper:
                    return False
        return True


# Precompiled patterns for typical Japanese range expressions
_PATTERNS: list[tuple[re.Pattern[str], callable]] = [
    (re.compile(r"^(\d+)から(\d+)$"),
     lambda m: Interval(
         lower=int(m.group(1)),
         upper=int(m.group(2)),
         lower_inclusive=True,
         upper_inclusive=True,
     )),
    (re.compile(r"^(\d+)以上(\d+)以下$"),
     lambda m: Interval(
         lower=int(m.group(1)),
         upper=int(m.group(2)),
         lower_inclusive=True,
         upper_inclusive=True,
     )),
    (re.compile(r"^(\d+)以上(\d+)未満$"),
     lambda m: Interval(
         lower=int(m.group(1)),
         upper=int(m.group(2)),
         lower_inclusive=True,
         upper_inclusive=False,
     )),
    (re.compile(r"^(\d+)より上$"),
     lambda m: Interval(
         lower=int(m.group(1)),
         upper=None,
         lower_inclusive=False,
         upper_inclusive=False,
     )),
    (re.compile(r"^(\d+)より下$"),
     lambda m: Interval(
         lower=None,
         upper=int(m.group(1)),
         lower_inclusive=False,
         upper_inclusive=False,
     )),
]


def parse_jp_range(text: str) -> Interval:
    """Parse a Japanese numeric range expression into an :class:`Interval`.

    Parameters
    ----------
    text:
        Japanese range expression such as ``"20から30"`` or ``"50より上"``.

    Returns
    -------
    Interval
        Parsed interval representation.

    Raises
    ------
    ValueError
        If the text cannot be parsed.
    """
    text = text.strip()
    for pattern, builder in _PATTERNS:
        m = pattern.fullmatch(text)
        if m:
            return builder(m)
    raise ValueError(f"Cannot parse range: {text}")
