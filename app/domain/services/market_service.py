from typing import Optional

import ccxt

from domain.entities.candles import Candle
from domain.entities.timestamps import TIMEFRAME
from domain.services.logging_service import AppLogger


class MarketDataService:
    def __init__(
        self,
        exchange_name: str = "kraken",
        timeframe: TIMEFRAME = TIMEFRAME.HOUR_1,
        logger: AppLogger | None = None,
    ):
        if timeframe.name not in TIMEFRAME.__members__:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        self.exchange_name = exchange_name
        self.timeframe = timeframe.ccxt_value
        self.exchange = getattr(ccxt, exchange_name)()
        self.timeframe_ms = timeframe.value
        self.logger = logger or AppLogger(None)

    def resolve_symbol(self, markets: dict, symbol: str) -> Optional[str]:
        resolved = symbol if symbol in markets else None
        if not resolved:
            self.logger.warning("Market symbol not found",
                                requested_symbol=symbol)
        return resolved

    def fetch_candles_page(
        self,
        symbol: str,
        since_ms: int,
        limit: int = 1000,
    ) -> list[Candle]:
        self.logger.debug(
            "Fetching candles page",
            symbol=symbol,
            since_ms=since_ms,
            limit=limit,
            timeframe=self.timeframe,
        )

        ohlcv = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=self.timeframe,
            since=since_ms,
            limit=limit,
        )

        candles = [
            Candle(
                timestamp=str(row[0]),
                symbol=symbol,
                open=row[1],
                high=row[2],
                low=row[3],
                close=row[4],
                volume=row[5],
            )
            for row in ohlcv
        ]

        self.logger.debug(
            "Fetched candles page",
            symbol=symbol,
            since_ms=since_ms,
            count=len(candles),
        )
        return candles

    def close(self) -> None:
        self.exchange.close()
        self.logger.info("Exchange client closed",
                         exchange_name=self.exchange_name)
