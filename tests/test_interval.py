import pandas as pd

from jp_range import Interval, parse_jp_range


def test_parse_inclusive_range():
    r = parse_jp_range("20から30")
    assert r.lower == 20
    assert r.upper == 30
    assert r.lower_inclusive is True
    assert r.upper_inclusive is True
    assert r.contains(20)
    assert r.contains(25)
    assert r.contains(30)
    assert not r.contains(19)
    assert not r.contains(31)


def test_parse_ge_le():
    r = parse_jp_range("30以上40以下")
    assert r.lower == 30
    assert r.upper == 40
    assert r.lower_inclusive is True
    assert r.upper_inclusive is True


def test_parse_ge_le_with_connector():
    r = parse_jp_range("30以上,40以下")
    assert r.lower == 30
    assert r.upper == 40
    assert r.lower_inclusive is True
    assert r.upper_inclusive is True


def test_parse_ge_le_with_word_connector():
    r = parse_jp_range("30以上そして40以下")
    assert r.lower == 30
    assert r.upper == 40
    assert r.lower_inclusive is True
    assert r.upper_inclusive is True


def test_parse_ge_lt():
    r = parse_jp_range("40以上50未満")
    assert r.lower == 40
    assert r.upper == 50
    assert r.lower_inclusive is True
    assert r.upper_inclusive is False
    assert r.contains(40)
    assert r.contains(49.9)
    assert not r.contains(50)


def test_greater_than():
    r = parse_jp_range("50より上")
    assert r.lower == 50
    assert r.upper is None
    assert not r.lower_inclusive
    assert r.contains(51)
    assert not r.contains(50)


def test_less_than():
    r = parse_jp_range("60より下")
    assert r.upper == 60
    assert r.lower is None
    assert not r.upper_inclusive
    assert r.contains(59)
    assert not r.contains(60)


def test_normalize_and_remove_spaces():
    r = parse_jp_range("\u3000４０  以上\u3000５０ 未満\u3000")
    assert r.lower == 40
    assert r.upper == 50
    assert r.lower_inclusive is True
    assert r.upper_inclusive is False


def test_tilde_connector():
    r = parse_jp_range("20〜30")
    assert r.lower == 20
    assert r.upper == 30


def test_exclusive_inclusive():
    r = parse_jp_range("70超90以下")
    assert r.lower == 70
    assert r.upper == 90
    assert not r.lower_inclusive
    assert r.upper_inclusive


def test_both_exclusive():
    r = parse_jp_range("10を超え20未満")
    assert not r.lower_inclusive
    assert not r.upper_inclusive
    assert r.contains(19.9)
    assert not r.contains(10)


def test_single_bound():
    r = parse_jp_range("80以上")
    assert r.lower == 80
    assert r.upper is None
    assert r.lower_inclusive


def test_single_bound_with_unit():
    r = parse_jp_range("１０個以上")
    assert r.lower == 10
    assert r.upper is None
    assert r.lower_inclusive


def test_upper_bound():
    r = parse_jp_range("100未満")
    assert r.upper == 100
    assert r.lower is None
    assert not r.upper_inclusive


def test_approx_range():
    r = parse_jp_range("90前後")
    assert round(r.lower, 1) == 85.5
    assert round(r.upper, 1) == 94.5


def test_approx_with_unit():
    r = parse_jp_range("90m程度")
    assert round(r.lower, 1) == 85.5
    assert round(r.upper, 1) == 94.5


def test_interval_notation():
    r = parse_jp_range("(2,3]")
    assert r.lower == 2
    assert r.upper == 3
    assert not r.lower_inclusive
    assert r.upper_inclusive


def test_max_min():
    r = parse_jp_range("最大10、最小マイナス5")
    assert r.lower == -5
    assert r.upper == 10
    assert r.lower_inclusive is True
    assert r.upper_inclusive is True


def test_max_value_min_value():
    r = parse_jp_range("最大値100 最小値10")
    assert r.lower == 10
    assert r.upper == 100
    assert r.lower_inclusive is True
    assert r.upper_inclusive is True


def test_dai_sho():
    r = parse_jp_range("大3,小1")
    assert r.lower == 1
    assert r.upper == 3


def test_parse_failure_returns_none():
    r = parse_jp_range("unknown")
    assert r is None


def test_to_pd_interval():
    interval = Interval(lower=1, upper=3, lower_inclusive=True, upper_inclusive=False)
    pd_interval = interval.to_pd_interval()
    assert isinstance(pd_interval, pd.Interval)
    assert pd_interval.left == 1
    assert pd_interval.right == 3
    assert pd_interval.closed == "left"
