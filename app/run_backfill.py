import logging
import os

from domain.entities.timestamps import TIMEFRAME
from domain.repositories.candle_repository import CandleRepository
from domain.repositories.db import get_session, init_db
from domain.services.backfill_service import HistoricalBackfillService
from domain.services.logging_service import AppLogger
from domain.services.market_service import MarketDataService


def setup_logging() -> AppLogger:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    base = logging.getLogger("trading-app")
    return AppLogger(base)


def stop_ccxt_debug_logging() -> None:
    # Keep third-party noise down even when LOG_LEVEL=DEBUG
    logging.getLogger("ccxt").setLevel(logging.WARNING)
    logging.getLogger("ccxt.base.exchange").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def run() -> None:
    app_logger = setup_logging()
    symbols = ["BTC/USD"]

    market_logger = app_logger.child(component="market")
    backfill_logger = app_logger.child(component="backfill")

    market_service = MarketDataService(
        exchange_name="bitstamp",
        timeframe=TIMEFRAME.HOUR_1,
        logger=market_logger,
    )

    init_db()

    try:
        for symbol in symbols:
            with get_session() as session:
                repo = CandleRepository(session)
                backfill_service = HistoricalBackfillService(
                    market_service=market_service,
                    candle_repo=repo,
                    logger=backfill_logger,
                )
                backfill_service.backfill_last_year(
                    symbols=[symbol],
                    page_limit=1000,
                )
    finally:
        market_service.close()


if __name__ == "__main__":
    run()
