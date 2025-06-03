# jp-range

jp-range is a small library for parsing Japanese numeric range expressions. It returns an `Interval` object implemented with [Pydantic](https://docs.pydantic.dev/) or ``None`` when parsing fails.

## Installation

```bash
pip install jp-range
# or install from GitHub
pip install git+https://github.com/first-automation/jp-range.git
```

Python 3.12 or later is required.

## Features

- Normalizes full width numbers and common punctuation
- Supports inclusive and exclusive bounds (`以上`, `未満`, etc.)
- Parses connectors such as `〜`, `-` and `から`
- Handles single-sided bounds, approximate expressions (`90前後`) and `A±d` notation
- Integrates with pandas via `apply_parse` for `Series` and `DataFrame`

## Usage

### Basic parsing

```python
from jp_range import parse

interval = parse("40以上50未満")
print(interval)               # [40, 50)
print(interval.contains(45))  # True
```

### Pandas integration

```python
from pandas import Series
from jp_range import apply_parse

# Convert Series of textual ranges to pandas.Interval
s = Series(["20～30", "50超", "未満100"])
result = apply_parse(s)
# result:
# 0     [20.0, 30.0]
# 1      (50.0, inf)
# 2    (-inf, 100.0)
# dtype: object

# Expand columns into numeric min/max
df = apply_parse(s.to_frame(name="range"), split_numeric=True)
# df:
#    range_max  range_min
# 0       30.0       20.0
# 1        NaN       50.0
# 2      100.0        NaN
```

### Supported expressions

- `"20から30"` – inclusive 20 to 30
- `"20〜30"` – inclusive 20 to 30 using a tilde connector
- `"30以上40以下"` – inclusive 30 to 40
- `"40以上50未満"` – 40 to under 50
- `"70超90以下"` – greater than 70 and up to 90
- `"50より上"` – greater than 50
- `"60より下"` – less than 60
- `"90前後"` – roughly around 90 (5% margin)
- `"(2,3]"` – standard interval notation

`parse_jp_range` returns ``None`` if the expression cannot be parsed.
