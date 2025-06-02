from pandas import Series, DataFrame, Interval as PdInterval

from jp_range import Interval, parse, parse_jp_range, parse_series


def test_parse_alias():
    r = parse("30以上40未満")
    expected = parse_jp_range("30以上40未満")
    assert r == expected


def test_parse_series_with_series():
    s = Series(["20～30", "50超", "未満100"])
    result = parse_series(s)
    assert isinstance(result, Series)
    assert isinstance(result.iloc[0], PdInterval)
    assert result.iloc[0].left == 20
    assert result.iloc[1].left == 50
    assert result.iloc[2].right == 100


def test_parse_series_with_dataframe():
    df = DataFrame({"range": ["20～30", "50超"]})
    result = parse_series(df)
    assert isinstance(result.loc[0, "range"], PdInterval)
    assert result.loc[0, "range"].left == 20

