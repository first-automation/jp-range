from pandas import Series, DataFrame

from jp_range import Interval, parse, parse_jp_range, parse_series


def test_parse_alias():
    r = parse("30以上40未満")
    expected = parse_jp_range("30以上40未満")
    assert r == expected


def test_parse_series_with_series():
    s = Series(["20～30", "50超", "未満100"])
    result = parse_series(s)
    assert isinstance(result, Series)
    assert isinstance(result.iloc[0], Interval)
    assert result.iloc[0].lower == 20
    assert result.iloc[1].lower == 50
    assert result.iloc[2].upper == 100


def test_parse_series_with_dataframe():
    df = DataFrame({"range": ["20～30", "50超"]})
    result = parse_series(df)
    assert isinstance(result.loc[0, "range"], Interval)
    assert result.loc[0, "range"].lower == 20
