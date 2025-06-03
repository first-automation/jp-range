from __future__ import annotations

from typing import Callable
import re

import neologdn

from .interval import Interval

# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------
# Characters that we *only* care about for connecting two numbers (range
# connectors).  We translate *every* variation we know of into a single ASCII
# hyphen ("-") so that the regex patterns downstream stay simple.
#
# Note that we include the ASCII tilde "~" because **neologdn** converts the
# full‑width wave‑dash U+301C (〜) into it.
_CONNECTOR_CHARS = "〜～~ー－−―‐"


def _normalize(text: str) -> str:  # noqa: D401
    """Return a *minimal* normalised representation for pattern matching."""

    # 1. *先に*コネクターだけ ASCII ハイフンに統一しておく。
    #    （neologdn が波ダッシュを "~" に変換してしまう前に潰す）
    text = re.sub(f"[{_CONNECTOR_CHARS}]", "-", text)

    # 2. neologdn で全角→半角・空白除去など共通処理
    text = neologdn.normalize(text)

    # 3. 数値の前に付く言葉を記号化（±, +, -）
    text = (
        text.replace("プラスマイナス", "±")
        .replace("マイナス", "-")
        .replace("プラス", "+")
    )

    # 4. 残った空白を完全に除去
    text = re.sub(r"\s+", "", text)

    return text


# Numeric pattern supporting optional decimal and sign with trailing units
_NUM = r"([-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?)(?:[a-zA-Zぁ-んァ-ン一-龥]*)"
# Separator pattern used between two numbers.  Excludes sign characters so
# that we don't swallow the sign of the next number.
_SEP = r"[^\d+-]*"


def _f(num: str) -> float:  # noqa: D401 short descr
    return float(num)


def _range_builder(
    lower_inclusive: bool, upper_inclusive: bool
) -> Callable[[re.Match[str]], Interval]:
    def _build(m: re.Match[str]) -> Interval:  # noqa: WPS430
        return Interval(
            lower=_f(m.group(1)),
            upper=_f(m.group(2)),
            lower_inclusive=lower_inclusive,
            upper_inclusive=upper_inclusive,
        )

    return _build


def _single_lower(inclusive: bool) -> Callable[[re.Match[str]], Interval]:
    def _build(m: re.Match[str]) -> Interval:  # noqa: WPS430
        return Interval(
            lower=_f(m.group(1)),
            upper=None,
            lower_inclusive=inclusive,
            upper_inclusive=False,
        )

    return _build


def _single_upper(inclusive: bool) -> Callable[[re.Match[str]], Interval]:
    def _build(m: re.Match[str]) -> Interval:  # noqa: WPS430
        return Interval(
            lower=None,
            upper=_f(m.group(1)),
            lower_inclusive=False,
            upper_inclusive=inclusive,
        )

    return _build


def _single_max(m: re.Match[str]) -> Interval:
    return Interval(
        lower=None, upper=_f(m.group(1)), lower_inclusive=False, upper_inclusive=True
    )


def _single_min(m: re.Match[str]) -> Interval:
    return Interval(
        lower=_f(m.group(1)), upper=None, lower_inclusive=True, upper_inclusive=False
    )


def _approx(m: re.Match[str]) -> Interval:  # noqa: D401
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


def _plus_minus_zero(m: re.Match[str]) -> Interval:  # ±10
    delta = _f(m.group(1))
    return Interval(
        lower=-delta, upper=delta, lower_inclusive=True, upper_inclusive=True
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
    return Interval(
        lower=_f(m.group(2)),
        upper=_f(m.group(1)),
        lower_inclusive=True,
        upper_inclusive=True,
    )


def _max_lower_lt(m: re.Match[str]) -> Interval:
    return Interval(
        lower=_f(m.group(2)),
        upper=_f(m.group(1)),
        lower_inclusive=False,
        upper_inclusive=True,
    )


_PATTERNS: list[tuple[re.Pattern[str], Callable[[re.Match[str]], Interval]]] = [
    (re.compile(rf"^([\(\[]){_NUM},{_NUM}([\)\]])$"), _interval_notation),
    (re.compile(rf"^{_NUM}から{_NUM}(?:まで)?$"), _range_builder(True, True)),
    (re.compile(rf"^{_NUM}[〜～\-－ー―‐]{{1}}{_NUM}$"), _range_builder(True, True)),
    (re.compile(rf"^{_NUM}と{_NUM}の?間$"), _range_builder(False, False)),
    (
        re.compile(rf"^(?:最大(?:値)?|大){_NUM}{_SEP}(?:最小(?:値)?|小){_NUM}$"),
        _max_min,
    ),
    (re.compile(rf"^(?:最大(?:値)?|大){_NUM}{_SEP}{_NUM}未満$"), _max_lower_lt),
    (re.compile(rf"^(?:最大(?:値)?|大){_NUM}$"), _single_max),
    (re.compile(rf"^(?:最小(?:値)?|小){_NUM}$"), _single_min),
    (re.compile(rf"^{_NUM}以上{_SEP}{_NUM}以下$"), _range_builder(True, True)),
    (re.compile(rf"^{_NUM}以上{_SEP}{_NUM}未満$"), _range_builder(True, False)),
    (re.compile(rf"^{_NUM}超{_SEP}{_NUM}以下$"), _range_builder(False, True)),
    (re.compile(rf"^{_NUM}超{_SEP}{_NUM}未満$"), _range_builder(False, False)),
    (re.compile(rf"^{_NUM}を?超え{_SEP}{_NUM}以下$"), _range_builder(False, True)),
    (re.compile(rf"^{_NUM}を?超え{_SEP}{_NUM}未満$"), _range_builder(False, False)),
    (re.compile(rf"^{_NUM}を?上回り{_SEP}{_NUM}以下$"), _range_builder(False, True)),
    (re.compile(rf"^{_NUM}を?上回り{_SEP}{_NUM}未満$"), _range_builder(False, False)),
    (re.compile(rf"^{_NUM}より大きい{_SEP}{_NUM}以下$"), _range_builder(False, True)),
    (re.compile(rf"^{_NUM}より大きい{_SEP}{_NUM}未満$"), _range_builder(False, False)),
    (re.compile(rf"^{_NUM}(?:以上|以降|以後|から)$"), _single_lower(True)),
    (
        re.compile(rf"^{_NUM}(?:超|を?超える|より大きい|より上|を?上回る)$"),
        _single_lower(False),
    ),
    (re.compile(rf"^{_NUM}(?:以下|以内|まで)$"), _single_upper(True)),
    (
        re.compile(rf"^{_NUM}(?:未満|より小さい|より下|を?下回る|未到達)$"),
        _single_upper(False),
    ),
    (re.compile(rf"^未満{_NUM}$"), _single_upper(False)),
    (re.compile(rf"^{_NUM}(?:前後|程度|くらい)$"), _approx),
    (re.compile(rf"^{_NUM}±{_NUM}$"), _plus_minus),
    (re.compile(rf"^±{_NUM}$"), _plus_minus_zero),
]


def _parse_atomic(segment: str) -> Interval | None:
    for pattern, builder in _PATTERNS:
        m = pattern.fullmatch(segment)
        if m:
            return builder(m)
    return None


def _try_parse_float(text: str) -> float | None:
    try:
        return float(text)
    except ValueError:
        return None


def parse_jp_range(
    text: str | int | float | tuple[int | float, ...] | list[int | float],
) -> Interval:
    if isinstance(text, (tuple, list)):
        return Interval(
            lower=min(text), upper=max(text), lower_inclusive=True, upper_inclusive=True
        )
    if isinstance(text, (int, float)):
        return Interval(
            lower=text, upper=text, lower_inclusive=True, upper_inclusive=True
        )
    if isinstance(text, str):
        num = _try_parse_float(text)
        if num is not None:
            return Interval(
                lower=num, upper=num, lower_inclusive=True, upper_inclusive=True
            )

    text = _normalize(text).strip()

    result = _parse_atomic(text)
    if result is not None:
        return result

    parts = [p for p in re.split(r"[、,，]", text) if p]
    if len(parts) > 1:
        intervals = []
        for part in parts:
            r = _parse_atomic(part)
            if r is None:
                return Interval()
            intervals.append(r)
        combined = intervals[0]
        for iv in intervals[1:]:
            combined = combined.intersect(iv)
        return combined

    for i in range(1, len(text)):
        left = _parse_atomic(text[:i])
        right = _parse_atomic(text[i:])
        if left is not None and right is not None:
            return left.intersect(right)

    return Interval()
