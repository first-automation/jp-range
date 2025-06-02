# jp-range

jp-range is a small library for parsing Japanese numeric range expressions. It returns an `Interval` object implemented with [Pydantic](https://docs.pydantic.dev/).

## Installation

```bash
pip install jp-range
# or install from GitHub
pip install git+https://github.com/neka-nat/jp-range.git
```

Python 3.12 or later is required.

## Features

- Normalizes full width numbers and common punctuation
- Supports inclusive and exclusive bounds (`以上`, `未満`, etc.)
- Parses connectors such as `〜`, `-` and `から`
- Handles single-sided bounds, approximate expressions (`90前後`) and `A±d` notation
- Integrates with pandas via `parse_series` for `Series` and `DataFrame`

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
from jp_range import parse_series

s = Series(["20～30", "50超", "未満100"])
result = parse_series(s)
# result is a Series of Interval objects
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

`parse_jp_range` raises `ValueError` if the expression cannot be parsed.
