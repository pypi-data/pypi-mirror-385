from collections.abc import Iterable

from pydantic import BaseModel

from ..adapters.base import PriceDataProvider
from ..schemas.models import PriceBar


class FacadeConfig(BaseModel):
    primary: str = "openbb"


class DataFacade:
    """
    DIP: depends on the abstraction (PriceDataProvider), not a concrete class.
    SRP: orchestration only (logging, validation, selection) — no provider logic here.
    """

    def __init__(
        self, price_provider: PriceDataProvider, config: FacadeConfig | None = None
    ) -> None:
        self.price_provider = price_provider
        self.config = config or FacadeConfig()

    async def get_price_bars(
        self, symbol: str, interval: str = "1d", limit: int = 100
    ) -> Iterable[PriceBar]:
        return await self.price_provider.get_price_bars(
            symbol=symbol, interval=interval, limit=limit
        )
