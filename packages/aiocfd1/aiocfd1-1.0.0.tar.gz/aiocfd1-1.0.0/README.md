# AIO CF D1

A simple asyncio wrapper for Cloudflare D1's REST API. It does nothing but query SQL.

# Install

```
pip install aiocfd1
```

# Usage

```python
from aiocfd1 import D1
import asyncio
# Get these credentials from cloudflare dashboard!
db = D1("account id", "token", "database id")
async def test():
    result = await db.execute("SELECT * FROM table; SELECT * FROM table WHERE something = 'test';")
    print(result)

asyncio.run(test())
```

## Output

```python
[
    [
        {
            "something": "lorem",
            "foo": "bar"
        },
        {
            "something": "test",
            "foo": "baz"
        },
        {
            "something": "abc",
            "foo": "qux"
        }
    ],
    [
        {
            "something": "test",
            "foo": "baz"
        }
    ]
]
```
