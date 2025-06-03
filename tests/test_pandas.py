from pandas import Series, DataFrame, Interval as PdInterval
import pandas as pd

from jp_range import parse, parse_jp_range, apply_parse, detect_interval_columns


def test_parse_alias():
    r = parse("30以上40未満")
    expected = parse_jp_range("30以上40未満")
    assert r == expected


def test_apply_parse_with_series():
    s = Series(["20～30", "50超", "未満100"])
    result = apply_parse(s)
    assert isinstance(result, Series)
    assert isinstance(result.iloc[0], PdInterval)
    assert result.iloc[0].left == 20
    assert result.iloc[1].left == 50
    assert result.iloc[2].right == 100


def test_apply_parse_with_dataframe():
    df = DataFrame({"range": ["20～30", "50超"]})
    result = apply_parse(df)
    assert isinstance(result.loc[0, "range"], PdInterval)
    assert result.loc[0, "range"].left == 20


def test_apply_parse_with_columns():
    df = DataFrame({"range": ["20～30", "50超"], "text": ["a", "b"]})
    result = apply_parse(df, columns=["range"])
    assert isinstance(result.loc[0, "range"], PdInterval)
    assert result.loc[0, "text"] == "a"


def test_detect_interval_columns():
    df = DataFrame({
        "a": ["20～30", "50超"],
        "b": ["foo", "bar"],
    })
    cols = detect_interval_columns(df, threshold=0.5)
    assert "a" in cols
    assert "b" not in cols


def test_apply_parse_split_numeric():
    df = DataFrame({"range": ["20～30", "50超"]})
    result = apply_parse(df, split_numeric=True)
    assert "range_max" in result.columns
    assert "range_min" in result.columns
    assert result.loc[0, "range_min"] == 20
    assert result.loc[0, "range_max"] == 30
    assert result.loc[1, "range_min"] == 50
    assert pd.isna(result.loc[1, "range_max"])

