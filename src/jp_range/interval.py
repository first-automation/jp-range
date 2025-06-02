from __future__ import annotations

from typing import Optional
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


# Precompiled patterns for various Japanese range expressions
_PATTERNS: list[tuple[re.Pattern[str], callable]] = [
    # 20から30 / 20から30まで
    (
        re.compile(fr"^{_NUM}から{_NUM}(?:まで)?$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=True,
            upper_inclusive=True,
        ),
    ),
    # 20〜30, 20-30, 20～30
    (
        re.compile(fr"^{_NUM}[〜～\-－ー―‐]{1}{_NUM}$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=True,
            upper_inclusive=True,
        ),
    ),
    # AとBの間
    (
        re.compile(fr"^{_NUM}と{_NUM}の?間$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=False,
            upper_inclusive=False,
        ),
    ),
    # A以上B以下
    (
        re.compile(fr"^{_NUM}以上{_NUM}以下$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=True,
            upper_inclusive=True,
        ),
    ),
    # A以上B未満
    (
        re.compile(fr"^{_NUM}以上{_NUM}未満$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=True,
            upper_inclusive=False,
        ),
    ),
    # A超B以下
    (
        re.compile(fr"^{_NUM}超{_NUM}以下$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=False,
            upper_inclusive=True,
        ),
    ),
    # A超B未満
    (
        re.compile(fr"^{_NUM}超{_NUM}未満$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=False,
            upper_inclusive=False,
        ),
    ),
    # Aを超えB以下
    (
        re.compile(fr"^{_NUM}を?超え{_NUM}以下$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=False,
            upper_inclusive=True,
        ),
    ),
    # Aを超えB未満
    (
        re.compile(fr"^{_NUM}を?超え{_NUM}未満$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=False,
            upper_inclusive=False,
        ),
    ),
    # Aを上回りB以下
    (
        re.compile(fr"^{_NUM}を?上回り{_NUM}以下$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=False,
            upper_inclusive=True,
        ),
    ),
    # Aを上回りB未満
    (
        re.compile(fr"^{_NUM}を?上回り{_NUM}未満$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=False,
            upper_inclusive=False,
        ),
    ),
    # Aより大きいB以下
    (
        re.compile(fr"^{_NUM}より大きい{_NUM}以下$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=False,
            upper_inclusive=True,
        ),
    ),
    # Aより大きいB未満
    (
        re.compile(fr"^{_NUM}より大きい{_NUM}未満$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=False,
            upper_inclusive=False,
        ),
    ),
    # Lower bound inclusive
    (
        re.compile(fr"^{_NUM}(?:以上|以降|以後|から)$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=None,
            lower_inclusive=True,
            upper_inclusive=False,
        ),
    ),
    # Lower bound exclusive
    (
        re.compile(fr"^{_NUM}(?:超|を?超える|より大きい|より上|を?上回る)$"),
        lambda m: Interval(
            lower=_f(m.group(1)),
            upper=None,
            lower_inclusive=False,
            upper_inclusive=False,
        ),
    ),
    # Upper bound inclusive
    (
        re.compile(fr"^{_NUM}(?:以下|以内|まで)$"),
        lambda m: Interval(
            lower=None,
            upper=_f(m.group(1)),
            lower_inclusive=False,
            upper_inclusive=True,
        ),
    ),
    # Upper bound exclusive
    (
        re.compile(fr"^{_NUM}(?:未満|より小さい|より下|を?下回る|未到達)$"),
        lambda m: Interval(
            lower=None,
            upper=_f(m.group(1)),
            lower_inclusive=False,
            upper_inclusive=False,
        ),
    ),
    # Approximate: A前後 / A程度 / Aくらい
    (
        re.compile(fr"^{_NUM}(?:前後|程度|くらい)$"),
        lambda m: Interval(
            lower=_f(m.group(1)) * 0.95,
            upper=_f(m.group(1)) * 1.05,
            lower_inclusive=True,
            upper_inclusive=True,
        ),
    ),
    # A±d
    (
        re.compile(fr"^{_NUM}±{_NUM}$"),
        lambda m: Interval(
            lower=_f(m.group(1)) - _f(m.group(2)),
            upper=_f(m.group(1)) + _f(m.group(2)),
            lower_inclusive=True,
            upper_inclusive=True,
        ),
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

