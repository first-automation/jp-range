from __future__ import annotations

from typing import Optional

import pandas as pd

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

    def is_empty(self) -> bool:
        """Return True if this interval is empty."""
        return self.lower is None and self.upper is None

    def has_range(self) -> bool:
        """Return True if this interval has a range."""
        return (
            (self.lower is None and self.upper is not None)
            or (self.lower is not None and self.upper is None)
            or (
                self.lower is not None
                and self.upper is not None
                and self.lower < self.upper
            )
        )

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

    def to_pd_interval(self) -> pd.Interval | None:
        """Return a :class:`pandas.Interval` representation of this interval."""
        if self.is_empty():
            return None
        if not self.has_range():
            return self.lower
        left = self.lower if self.lower is not None else float("-inf")
        right = self.upper if self.upper is not None else float("inf")
        if self.lower_inclusive and self.upper_inclusive:
            closed = "both"
        elif self.lower_inclusive:
            closed = "left"
        elif self.upper_inclusive:
            closed = "right"
        else:
            closed = "neither"
        return pd.Interval(left, right, closed=closed)

    def intersect(self, other: "Interval") -> "Interval":
        """Return the intersection of this interval with another."""
        lower = self.lower
        lower_inc = self.lower_inclusive
        if other.lower is not None:
            if (
                lower is None
                or other.lower > lower
                or (other.lower == lower and not other.lower_inclusive)
            ):
                lower = other.lower
                lower_inc = other.lower_inclusive
            elif other.lower == lower:
                lower_inc = lower_inc and other.lower_inclusive

        upper = self.upper
        upper_inc = self.upper_inclusive
        if other.upper is not None:
            if (
                upper is None
                or other.upper < upper
                or (other.upper == upper and not other.upper_inclusive)
            ):
                upper = other.upper
                upper_inc = other.upper_inclusive
            elif other.upper == upper:
                upper_inc = upper_inc and other.upper_inclusive

        return Interval(
            lower=lower,
            upper=upper,
            lower_inclusive=lower_inc,
            upper_inclusive=upper_inc,
        )
