from domain.entities import TIMEFRAME
from app.domain.repositories.candle_repository import CandleRepository
from app.domain.repositories.db import get_session, init_db
from app.domain.services.backfill_service import HistoricalBackfillService
from app.domain.services.market_service import MarketDataService


def run() -> None:
    symbols = ["BTC/CAD"]

    init_db()

    market_service = MarketDataService(
        exchange_name="kraken",
        timeframe=TIMEFRAME.HOUR_1,
    )

    try:
        for symbol in symbols:
            with get_session() as session:
                repo = CandleRepository(session)
                backfill_service = HistoricalBackfillService(
                    market_service, repo)
                backfill_service.backfill_last_year(
                    symbols=[symbol], page_limit=1000)
    finally:
        market_service.close()


if __name__ == "__main__":
    run()
