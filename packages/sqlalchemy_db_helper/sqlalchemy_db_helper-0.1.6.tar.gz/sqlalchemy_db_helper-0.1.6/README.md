Example:
```python
from sqlalchemy_db_helper import db_startup, db_shutdown


async def startup() -> None:
    await db_startup("sqlite+aiosqlite:///projects/analytic.sqlite")


async def shutdown() -> None:
    await db_shutdown()


async def main() -> None:
    await startup()
    ...
    await shutdown()


if __name__ == "__main__":
    from asyncio import run

    run(main())

```
