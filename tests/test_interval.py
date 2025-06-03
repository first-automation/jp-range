import pandas as pd
import pytest

from jp_range import Interval, parse_jp_range


@pytest.mark.parametrize(
    "text, lower, upper, lower_inc, upper_inc, contains, not_contains",
    [
        ("", None, None, False, False, [], []),
        (1, 1, 1, True, True, [1], []),
        ("20から30", 20, 30, True, True, [20, 25, 30], [19, 31]),
        ("30以上40以下", 30, 40, True, True, [], []),
        ("30以上,40以下", 30, 40, True, True, [], []),
        ("30以上そして40以下", 30, 40, True, True, [], []),
        ("40以上50未満", 40, 50, True, False, [40, 49.9], [50]),
        ("50より上", 50, None, False, False, [51], [50]),
        ("60より下", None, 60, False, False, [59], [60]),
        ("\u3000４０  以上\u3000５０ 未満\u3000", 40, 50, True, False, [], []),
        ("20〜30", 20, 30, True, True, [], []),
        ("70超90以下", 70, 90, False, True, [], []),
        ("10を超え20未満", 10, 20, False, False, [19.9], [10]),
        ("80以上", 80, None, True, False, [], []),
        ("１０個以上", 10, None, True, False, [], []),
        ("100未満", None, 100, False, False, [], []),
        ("90前後", 85.5, 94.5, True, True, [], []),
        ("90m程度", 85.5, 94.5, True, True, [], []),
        ("±10", -10, 10, True, True, [], []),
        ("プラスマイナス10", -10, 10, True, True, [], []),
        ("1±0.1", 0.9, 1.1, True, True, [], []),
        ("1プラスマイナス0.1", 0.9, 1.1, True, True, [], []),
        ("(2,3]", 2, 3, False, True, [], []),
        ("最大10、最小マイナス5", -5, 10, True, True, [], []),
        ("最大値100 最小値10", 10, 100, True, True, [], []),
        ("大3,小1", 1, 3, True, True, [], []),
        ("最大10,-5未満", -5, 10, False, True, [], []),
        ("5以上、最小1", 5, None, True, False, [], []),
        ("１００より上、小10", 100, None, False, False, [], []),
        ("30以下20以上", 20, 30, True, True, [], []),
        ("最小-5最大５０", -5, 50, True, True, [], []),
    ],
)
def test_parse_ranges(text, lower, upper, lower_inc, upper_inc, contains, not_contains):
    r = parse_jp_range(text)
    assert isinstance(r, Interval)
    if lower is None:
        assert r.lower is None
    else:
        assert r.lower == pytest.approx(lower)
    if upper is None:
        assert r.upper is None
    else:
        assert r.upper == pytest.approx(upper)
    assert r.lower_inclusive is lower_inc
    assert r.upper_inclusive is upper_inc
    for v in contains:
        assert r.contains(v)
    for v in not_contains:
        assert not r.contains(v)


def test_parse_failure_returns_empty_interval():
    r = parse_jp_range("unknown")
    assert r.lower is None
    assert r.upper is None
    assert not r.has_range()


def test_to_pd_interval():
    interval = Interval(lower=1, upper=3, lower_inclusive=True, upper_inclusive=False)
    pd_interval = interval.to_pd_interval()
    assert isinstance(pd_interval, pd.Interval)
    assert pd_interval.left == 1
    assert pd_interval.right == 3
    assert pd_interval.closed == "left"
