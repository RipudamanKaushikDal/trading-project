from typing import Optional

from domain.entities import Candle, TIMEFRAME
import ccxt


class MarketDataService:

    def __init__(self, exchange_name: str = "kraken", timeframe: TIMEFRAME = TIMEFRAME.HOUR_1):
        if timeframe.name not in TIMEFRAME.__members__:
            raise ValueError(f"Unsupported timeframe: {timeframe}")

        self.exchange_name = exchange_name
        self.timeframe = timeframe.ccxt_value
        self.exchange = getattr(ccxt, exchange_name)()
        self.timeframe_ms = timeframe.value

    def resolve_symbol(self, markets: dict, symbol: str) -> Optional[str]:
        return symbol if symbol in markets else None

    def fetch_candles_page(
        self,
        symbol: str,
        since_ms: int,
        limit: int = 1000,
    ) -> list[Candle]:
        ohlcv = self.exchange.fetch_ohlcv(
            symbol,
            timeframe=self.timeframe,
            since=since_ms,
            limit=limit,
        )
        return [
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

    def close(self) -> None:
        self.exchange.close()
