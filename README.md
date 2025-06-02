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
- ``"30以上40以下"`` – inclusive 30 to 40
- ``"40以上50未満"`` – 40 to under 50
- ``"50より上"`` – greater than 50
- ``"60より下"`` – less than 60
