# datetoolz

Tiny date helper library - get today, yesterday, tomorrow, weekday, etc.

## Install (editable)

```bash
pip install -e .
```

## Usage

```python
from datetoolz import today, yesterday
print(today())     # 2025-10-20
print(yesterday()) # 2025-10-19
```

### API

- today() -> str: ISO date YYYY-MM-DD
- yesterday() -> str: ISO date YYYY-MM-DD
- tomorrow() -> str: ISO date YYYY-MM-DD
- weekday(fmt: Literal["name","abbr","index"]) -> str | int
