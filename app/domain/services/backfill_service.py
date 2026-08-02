import time
from datetime import UTC, datetime, timedelta
from typing import Iterable

from app.domain.repositories.candle_repository import CandleRepository
from app.domain.services.market_service import MarketDataService


class HistoricalBackfillService:
    def __init__(self, market_service: MarketDataService, candle_repo: CandleRepository):
        self.market_service = market_service
        self.candle_repo = candle_repo

    def backfill_last_year(
        self,
        symbols: Iterable[str],
        end_time: datetime | None = None,
        page_limit: int = 1000,
        max_retries: int = 3,
    ) -> None:

        end_dt = end_time.astimezone(UTC) if end_time else datetime.now(UTC)
        start_dt = end_dt - timedelta(days=365)

        start_ms = int(start_dt.timestamp() * 1000)
        end_ms = int(end_dt.timestamp() * 1000)
        tf_ms = self.market_service.timeframe_ms

        markets = self.market_service.exchange.load_markets()

        for requested_symbol in symbols:
            symbol = self.market_service.resolve_symbol(
                markets, requested_symbol)
            if not symbol:
                print(f"Skipping missing market: {requested_symbol}")
                continue

            cursor = start_ms
            while cursor <= end_ms:
                candles: list = []
                for attempt in range(1, max_retries + 1):
                    try:
                        candles = self.market_service.fetch_candles_page(
                            symbol=symbol,
                            since_ms=cursor,
                            limit=page_limit,
                        )
                        break
                    except Exception as exc:
                        if attempt == max_retries:
                            raise RuntimeError(
                                f"Failed fetching candles for {symbol} after {max_retries} retries."
                            ) from exc
                        time.sleep(attempt)

                if not candles:
                    print(f"No more candles for {symbol} after {cursor}.")
                    break

                bounded_candles = [
                    candle for candle in candles if int(candle.timestamp) <= end_ms
                ]
                if not bounded_candles:
                    break

                self.candle_repo.upsert_many(
                    bounded_candles,
                    self.market_service.timeframe,
                )
                print(
                    f"Inserted {len(bounded_candles)} candles for {symbol} starting at {cursor}."
                )

                next_cursor = int(candles[-1].timestamp) + tf_ms
                if next_cursor <= cursor:
                    print(f"Stopping {symbol}: cursor did not advance.")
                    break
                cursor = next_cursor

                rate_limit_ms = getattr(
                    self.market_service.exchange, "rateLimit", 0)
                if rate_limit_ms > 0:
                    time.sleep(rate_limit_ms / 1000)
