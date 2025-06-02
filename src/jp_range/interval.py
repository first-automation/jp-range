from __future__ import annotations

from typing import Callable, Optional
import re

from pydantic import BaseModel
import neologdn


def _normalize(text: str) -> str:
    """Normalize text for pattern matching."""
    text = neologdn.normalize(text)
    text = re.sub(r"\s+", "", text)
    table = str.maketrans(
        {
            "０": "0",
            "１": "1",
            "２": "2",
            "３": "3",
            "４": "4",
            "５": "5",
            "６": "6",
            "７": "7",
            "８": "8",
            "９": "9",
            "－": "-",
            "ー": "-",
            "−": "-",
            "―": "-",
            "‐": "-",
            "．": ".",
            "，": "",
            ",": "",
        }
    )
    return text.translate(table)


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


# Numeric pattern supporting optional decimal and sign
_NUM = r"([-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?)"


def _f(num: str) -> float:
    """Convert numeric string to float."""
    return float(num)


def _range_builder(
    lower_inclusive: bool, upper_inclusive: bool
) -> Callable[[re.Match[str]], "Interval"]:
    """Return a builder for a simple numeric range."""

    def _build(m: re.Match[str]) -> "Interval":
        return Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=lower_inclusive,
            upper_inclusive=upper_inclusive,
        )

    return _build


def _single_lower(inclusive: bool) -> Callable[[re.Match[str]], "Interval"]:
    """Return a builder for a lower bound only."""

    def _build(m: re.Match[str]) -> "Interval":
        return Interval(
            lower=_f(m.group(1)),
            upper=None,
            lower_inclusive=inclusive,
            upper_inclusive=False,
        )

    return _build


def _single_upper(inclusive: bool) -> Callable[[re.Match[str]], "Interval"]:
    """Return a builder for an upper bound only."""

    def _build(m: re.Match[str]) -> "Interval":
        return Interval(
            lower=None,
            upper=_f(m.group(1)),
            lower_inclusive=False,
            upper_inclusive=inclusive,
        )

    return _build


def _approx(m: re.Match[str]) -> "Interval":
    val = _f(m.group(1))
    return Interval(
        lower=val * 0.95, upper=val * 1.05, lower_inclusive=True, upper_inclusive=True
    )


def _plus_minus(m: re.Match[str]) -> "Interval":
    val = _f(m.group(1))
    delta = _f(m.group(2))
    return Interval(
        lower=val - delta, upper=val + delta, lower_inclusive=True, upper_inclusive=True
    )


# Precompiled patterns for various Japanese range expressions
_PATTERNS: list[tuple[re.Pattern[str], Callable[[re.Match[str]], Interval]]] = [
    # 20から30 / 20から30まで
    (
        re.compile(rf"^{_NUM}から{_NUM}(?:まで)?$"),
        _range_builder(True, True),
    ),
    # 20〜30, 20-30, 20～30
    (
        re.compile(rf"^{_NUM}[〜～\-－ー―‐]{1}{_NUM}$"),
        _range_builder(True, True),
    ),
    # AとBの間
    (
        re.compile(rf"^{_NUM}と{_NUM}の?間$"),
        _range_builder(False, False),
    ),
    # A以上B以下
    (
        re.compile(rf"^{_NUM}以上{_NUM}以下$"),
        _range_builder(True, True),
    ),
    # A以上B未満
    (
        re.compile(rf"^{_NUM}以上{_NUM}未満$"),
        _range_builder(True, False),
    ),
    # A超B以下
    (
        re.compile(rf"^{_NUM}超{_NUM}以下$"),
        _range_builder(False, True),
    ),
    # A超B未満
    (
        re.compile(rf"^{_NUM}超{_NUM}未満$"),
        _range_builder(False, False),
    ),
    # Aを超えB以下
    (
        re.compile(rf"^{_NUM}を?超え{_NUM}以下$"),
        _range_builder(False, True),
    ),
    # Aを超えB未満
    (
        re.compile(rf"^{_NUM}を?超え{_NUM}未満$"),
        _range_builder(False, False),
    ),
    # Aを上回りB以下
    (
        re.compile(rf"^{_NUM}を?上回り{_NUM}以下$"),
        _range_builder(False, True),
    ),
    # Aを上回りB未満
    (
        re.compile(rf"^{_NUM}を?上回り{_NUM}未満$"),
        _range_builder(False, False),
    ),
    # Aより大きいB以下
    (
        re.compile(rf"^{_NUM}より大きい{_NUM}以下$"),
        _range_builder(False, True),
    ),
    # Aより大きいB未満
    (
        re.compile(rf"^{_NUM}より大きい{_NUM}未満$"),
        _range_builder(False, False),
    ),
    # Lower bound inclusive
    (
        re.compile(rf"^{_NUM}(?:以上|以降|以後|から)$"),
        _single_lower(True),
    ),
    # Lower bound exclusive
    (
        re.compile(rf"^{_NUM}(?:超|を?超える|より大きい|より上|を?上回る)$"),
        _single_lower(False),
    ),
    # Upper bound inclusive
    (
        re.compile(rf"^{_NUM}(?:以下|以内|まで)$"),
        _single_upper(True),
    ),
    # Upper bound exclusive
    (
        re.compile(rf"^{_NUM}(?:未満|より小さい|より下|を?下回る|未到達)$"),
        _single_upper(False),
    ),
    # Approximate: A前後 / A程度 / Aくらい
    (
        re.compile(rf"^{_NUM}(?:前後|程度|くらい)$"),
        _approx,
    ),
    # A±d
    (
        re.compile(rf"^{_NUM}±{_NUM}$"),
        _plus_minus,
    ),
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
    text = _normalize(text)
    text = text.strip()
    for pattern, builder in _PATTERNS:
        m = pattern.fullmatch(text)
        if m:
            return builder(m)
    raise ValueError(f"Cannot parse range: {text}")
