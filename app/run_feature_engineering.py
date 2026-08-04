import logging
import os
from datetime import UTC, datetime, timedelta

from domain.entities.timestamps import TIMEFRAME
from domain.repositories.candle_feature_repository import CandleFeatureRepository
from domain.repositories.candle_repository import CandleRepository
from domain.repositories.db import get_session, init_db
from domain.services.feature_engineering_service import CandleFeatureEngineeringService
from domain.services.logging_service import AppLogger


def setup_logging() -> AppLogger:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    base = logging.getLogger("trading-app")
    return AppLogger(base)


def run() -> None:
    app_logger = setup_logging()
    symbols = ["BTC/CAD"]
    timeframe = TIMEFRAME.HOUR_1.ccxt_value

    end_time = datetime.now(UTC)
    start_time = end_time - timedelta(days=365)

    init_db()

    with get_session() as session:
        candle_repo = CandleRepository(session)
        feature_repo = CandleFeatureRepository(session)
        feature_service = CandleFeatureEngineeringService(
            candle_repo=candle_repo,
            feature_repo=feature_repo,
            logger=app_logger.child(component="feature_engineering"),
        )

        for symbol in symbols:
            count = feature_service.build_and_store(
                symbol=symbol,
                timeframe=timeframe,
                start_time=start_time,
                end_time=end_time,
            )
            app_logger.info(
                "Feature engineering completed for symbol",
                symbol=symbol,
                timeframe=timeframe,
                count=count,
            )


if __name__ == "__main__":
    run()
