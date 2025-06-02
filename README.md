# jp-range

A small utility to parse Japanese numeric range expressions.
The returned `Interval` is a [Pydantic](https://docs.pydantic.dev/) model.

## Usage

```python
from jp_range import parse_jp_range

interval = parse_jp_range("40以上50未満")
print(interval)
print(interval.contains(45))  # True
```

Supported expressions include:

- ``"20から30"`` – inclusive 20 to 30
- ``"20〜30"`` – inclusive 20 to 30 using a tilde connector
- ``"30以上40以下"`` – inclusive 30 to 40
- ``"40以上50未満"`` – 40 to under 50
- ``"70超90以下"`` – greater than 70 and up to 90
- ``"50より上"`` – greater than 50
- ``"60より下"`` – less than 60
- ``"90前後"`` – roughly around 90 (5% margin)
