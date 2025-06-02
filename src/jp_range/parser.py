from __future__ import annotations

from typing import Callable
import re

import neologdn

from .interval import Interval


def _normalize(text: str) -> str:
    """Normalize text for pattern matching."""
    # Preserve range connectors by replacing tildes before normalization
    text = text.replace("〜", "-").replace("～", "-")
    text = neologdn.normalize(text)
    text = text.replace("マイナス", "-").replace("プラス", "+")
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
        }
    )
    return text.translate(table)


# Numeric pattern supporting optional decimal and sign with trailing units
# Units such as "m" or "個" should not be captured as part of the numeric value
# but may appear directly after the number.
_NUM = r"([-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?)(?:[a-zA-Zぁ-んァ-ン一-龥]*)"


def _f(num: str) -> float:
    """Convert numeric string to float."""
    return float(num)


def _range_builder(
    lower_inclusive: bool, upper_inclusive: bool
) -> Callable[[re.Match[str]], Interval]:
    """Return a builder for a simple numeric range."""

    def _build(m: re.Match[str]) -> Interval:
        return Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=lower_inclusive,
            upper_inclusive=upper_inclusive,
        )

    return _build


def _single_lower(inclusive: bool) -> Callable[[re.Match[str]], Interval]:
    """Return a builder for a lower bound only."""

    def _build(m: re.Match[str]) -> Interval:
        return Interval(
            lower=_f(m.group(1)),
            upper=None,
            lower_inclusive=inclusive,
            upper_inclusive=False,
        )

    return _build


def _single_upper(inclusive: bool) -> Callable[[re.Match[str]], Interval]:
    """Return a builder for an upper bound only."""

    def _build(m: re.Match[str]) -> Interval:
        return Interval(
            lower=None,
            upper=_f(m.group(1)),
            lower_inclusive=False,
            upper_inclusive=inclusive,
        )

    return _build


def _single_max(m: re.Match[str]) -> Interval:
    """Return a builder for '最大A' or '大A'."""
    return Interval(
        lower=None, upper=_f(m.group(1)), lower_inclusive=False, upper_inclusive=True
    )


def _single_min(m: re.Match[str]) -> Interval:
    """Return a builder for '最小B' or '小B'."""
    return Interval(
        lower=_f(m.group(1)), upper=None, lower_inclusive=True, upper_inclusive=False
    )


def _approx(m: re.Match[str]) -> Interval:
    val = _f(m.group(1))
    return Interval(
        lower=val * 0.95, upper=val * 1.05, lower_inclusive=True, upper_inclusive=True
    )


def _plus_minus(m: re.Match[str]) -> Interval:
    val = _f(m.group(1))
    delta = _f(m.group(2))
    return Interval(
        lower=val - delta, upper=val + delta, lower_inclusive=True, upper_inclusive=True
    )


def _interval_notation(m: re.Match[str]) -> Interval:
    left, lower, upper, right = m.groups()
    return Interval(
        lower=_f(lower),
        upper=_f(upper),
        lower_inclusive=left == "[",
        upper_inclusive=right == "]",
    )


def _max_min(m: re.Match[str]) -> Interval:
    """Build Interval from patterns like '最大10最小1'."""
    return Interval(
        lower=_f(m.group(2)),
        upper=_f(m.group(1)),
        lower_inclusive=True,
        upper_inclusive=True,
    )


def _max_lower_lt(m: re.Match[str]) -> Interval:
    """Build Interval from patterns like '最大10、-5未満'."""
    return Interval(
        lower=_f(m.group(2)),
        upper=_f(m.group(1)),
        lower_inclusive=False,
        upper_inclusive=True,
    )


# Precompiled patterns for various Japanese range expressions
_PATTERNS: list[tuple[re.Pattern[str], Callable[[re.Match[str]], Interval]]] = [
    # Standard interval notation like "(2,3]" or "[1,5)"
    (
        re.compile(rf"^([\(\[]){_NUM},{_NUM}([\)\]])$"),
        _interval_notation,
    ),
    # 20から30 / 20から30まで
    (
        re.compile(rf"^{_NUM}から{_NUM}(?:まで)?$"),
        _range_builder(True, True),
    ),
    # 20〜30, 20-30, 20～30
    (
        re.compile(rf"^{_NUM}[〜～\-－ー―‐]{{1}}{_NUM}$"),
        _range_builder(True, True),
    ),
    # AとBの間
    (
        re.compile(rf"^{_NUM}と{_NUM}の?間$"),
        _range_builder(False, False),
    ),
    # 最大A、最小B / 最大値A 最小値B / 大A小B
    (
        re.compile(rf"^(?:最大(?:値)?|大){_NUM}\D*(?:最小(?:値)?|小){_NUM}$"),
        _max_min,
    ),
    # 最大A、B未満
    (
        re.compile(rf"^(?:最大(?:値)?|大){_NUM}\D*{_NUM}未満$"),
        _max_lower_lt,
    ),
    # 最大A
    (
        re.compile(rf"^(?:最大(?:値)?|大){_NUM}$"),
        _single_max,
    ),
    # 最小B
    (
        re.compile(rf"^(?:最小(?:値)?|小){_NUM}$"),
        _single_min,
    ),
    # A以上B以下 (allow connectors like commas or words between bounds)
    (
        re.compile(rf"^{_NUM}以上\D*{_NUM}以下$"),
        _range_builder(True, True),
    ),
    # A以上B未満
    (
        re.compile(rf"^{_NUM}以上\D*{_NUM}未満$"),
        _range_builder(True, False),
    ),
    # A超B以下
    (
        re.compile(rf"^{_NUM}超\D*{_NUM}以下$"),
        _range_builder(False, True),
    ),
    # A超B未満
    (
        re.compile(rf"^{_NUM}超\D*{_NUM}未満$"),
        _range_builder(False, False),
    ),
    # Aを超えB以下
    (
        re.compile(rf"^{_NUM}を?超え\D*{_NUM}以下$"),
        _range_builder(False, True),
    ),
    # Aを超えB未満
    (
        re.compile(rf"^{_NUM}を?超え\D*{_NUM}未満$"),
        _range_builder(False, False),
    ),
    # Aを上回りB以下
    (
        re.compile(rf"^{_NUM}を?上回り\D*{_NUM}以下$"),
        _range_builder(False, True),
    ),
    # Aを上回りB未満
    (
        re.compile(rf"^{_NUM}を?上回り\D*{_NUM}未満$"),
        _range_builder(False, False),
    ),
    # Aより大きいB以下
    (
        re.compile(rf"^{_NUM}より大きい\D*{_NUM}以下$"),
        _range_builder(False, True),
    ),
    # Aより大きいB未満
    (
        re.compile(rf"^{_NUM}より大きい\D*{_NUM}未満$"),
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
    # Upper bound with keyword before the number (e.g. "未満100")
    (
        re.compile(rf"^未満{_NUM}$"),
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
    Interval | None
        Parsed interval representation, or ``None`` if the text cannot be
        parsed.
    """
    text = _normalize(text)
    text = text.strip()

    def _parse_atomic(segment: str) -> Interval | None:
        for pattern, builder in _PATTERNS:
            m = pattern.fullmatch(segment)
            if m:
                return builder(m)
        return None

    result = _parse_atomic(text)
    if result is not None:
        return result

    parts = [p for p in re.split(r"[、,，]", text) if p]
    if len(parts) > 1:
        intervals = []
        for part in parts:
            r = _parse_atomic(part)
            if r is None:
                return None
            intervals.append(r)

        def _intersect(a: Interval, b: Interval) -> Interval:
            lower = a.lower
            lower_inc = a.lower_inclusive
            if b.lower is not None:
                if (
                    lower is None
                    or b.lower > lower
                    or (b.lower == lower and not b.lower_inclusive)
                ):
                    lower = b.lower
                    lower_inc = b.lower_inclusive
                elif b.lower == lower:
                    lower_inc = lower_inc and b.lower_inclusive

            upper = a.upper
            upper_inc = a.upper_inclusive
            if b.upper is not None:
                if (
                    upper is None
                    or b.upper < upper
                    or (b.upper == upper and not b.upper_inclusive)
                ):
                    upper = b.upper
                    upper_inc = b.upper_inclusive
                elif b.upper == upper:
                    upper_inc = upper_inc and b.upper_inclusive

            return Interval(
                lower=lower,
                upper=upper,
                lower_inclusive=lower_inc,
                upper_inclusive=upper_inc,
            )

        combined = intervals[0]
        for iv in intervals[1:]:
            combined = _intersect(combined, iv)
        return combined

    return None
