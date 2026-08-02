import time
from datetime import UTC, datetime, timedelta
from typing import Iterable

from domain.repositories.candle_repository import CandleRepository
from domain.services.logging_service import AppLogger
from domain.services.market_service import MarketDataService


class HistoricalBackfillService:
    def __init__(
        self,
        market_service: MarketDataService,
        candle_repo: CandleRepository,
        logger: AppLogger | None = None,
    ):
        self.market_service = market_service
        self.candle_repo = candle_repo
        self.logger = logger or AppLogger(None)

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

        self.logger.info(
            "Starting historical backfill",
            start_ms=start_ms,
            end_ms=end_ms,
            timeframe=self.market_service.timeframe,
            symbols=list(symbols),
        )

        markets = self.market_service.exchange.load_markets()

        for requested_symbol in symbols:
            symbol = self.market_service.resolve_symbol(
                markets, requested_symbol)
            if not symbol:
                self.logger.warning(
                    "Skipping missing market",
                    requested_symbol=requested_symbol,
                )
                continue

            symbol_logger = self.logger.child(symbol=symbol)

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
                            symbol_logger.exception(
                                "Failed fetching candles after retries",
                                cursor=cursor,
                                max_retries=max_retries,
                            )
                            raise RuntimeError(
                                f"Failed fetching candles for {symbol} after {max_retries} retries."
                            ) from exc
                        symbol_logger.warning(
                            "Fetch failed; retrying",
                            cursor=cursor,
                            attempt=attempt,
                            max_retries=max_retries,
                        )
                        time.sleep(attempt)

                if not candles:
                    symbol_logger.info(
                        "No more candles returned", cursor=cursor)
                    break

                bounded_candles = [
                    candle for candle in candles if int(candle.timestamp) <= end_ms
                ]
                if not bounded_candles:
                    symbol_logger.info(
                        "Reached end time boundary",
                        cursor=cursor,
                        end_ms=end_ms,
                    )
                    break

                self.candle_repo.upsert_many(
                    bounded_candles,
                    self.market_service.timeframe,
                )
                symbol_logger.info(
                    "Upserted candles",
                    cursor=cursor,
                    count=len(bounded_candles),
                )

                next_cursor = int(candles[-1].timestamp) + \
                    self.market_service.timeframe_ms
                if next_cursor <= cursor:
                    symbol_logger.warning(
                        "Stopping because cursor did not advance",
                        cursor=cursor,
                        next_cursor=next_cursor,
                    )
                    break
                cursor = next_cursor

                rate_limit_ms = getattr(
                    self.market_service.exchange, "rateLimit", 0)
                if rate_limit_ms > 0:
                    symbol_logger.debug(
                        "Sleeping for exchange rate limit",
                        cursor=cursor,
                        rate_limit_ms=rate_limit_ms,
                    )
                    time.sleep(rate_limit_ms / 1000)
