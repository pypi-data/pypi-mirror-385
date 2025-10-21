# tests/utils/factories.py
from datetime import datetime, timezone
from decimal import Decimal
from market_data_pipeline.types import Quote


def utc(ts: float | int) -> datetime:
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def make_tick(
    symbol: str = "NVDA",
    price: Decimal | float = 100.0,
    size: Decimal | float = 1,
    ts: float | int | None = None,
    source: str = "synthetic",
    metadata: dict | None = None,
) -> Quote:
    if not isinstance(price, Decimal):
        from decimal import Decimal as D

        price = D(str(price))
    if not isinstance(size, Decimal):
        from decimal import Decimal as D

        size = D(str(size))
    dt = utc(ts) if ts is not None else datetime.now(timezone.utc)
    return Quote(
        symbol=symbol,
        price=price,
        size=size,
        timestamp=dt,
        source=source,
        metadata=metadata or {},
    )
