from datetime import UTC, datetime
from decimal import Decimal
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from domain.entities import Candle
from app.domain.models.candles import CandleRow


class CandleRepository:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _parse_open_time(timestamp_ms: str) -> datetime:
        ms = int(timestamp_ms)
        return datetime.fromtimestamp(ms / 1000, tz=UTC)

    def _build_candle_from_row(self, row: CandleRow) -> Candle:
        return Candle(
            timestamp=str(int(row.open_time.timestamp() * 1000)),
            symbol=row.symbol,
            open=float(row.open),
            high=float(row.high),
            low=float(row.low),
            close=float(row.close),
            volume=float(row.volume),
        )

    def upsert_many(self, candles: Iterable[Candle], timeframe: str) -> None:
        rows = [
            {
                "symbol": candle.symbol,
                "timeframe": timeframe,
                "open_time": self._parse_open_time(candle.timestamp),
                "open": Decimal(str(candle.open)),
                "high": Decimal(str(candle.high)),
                "low": Decimal(str(candle.low)),
                "close": Decimal(str(candle.close)),
                "volume": Decimal(str(candle.volume)),
            }
            for candle in candles
        ]

        if not rows:
            return

        stmt = insert(CandleRow).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["symbol", "timeframe", "open_time"],
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "volume": stmt.excluded.volume,
            },
        )
        self.session.execute(stmt)

    def get_candles(
        self, symbol: str, timeframe: str, start_time: datetime, end_time: datetime
    ) -> Iterable[Candle]:
        stmt = (
            select(CandleRow)
            .where(
                CandleRow.symbol == symbol,
                CandleRow.timeframe == timeframe,
                CandleRow.open_time >= start_time.replace(tzinfo=UTC),
                CandleRow.open_time <= end_time.replace(tzinfo=UTC),
            )
            .order_by(CandleRow.open_time)
        )
        result = self.session.execute(stmt).scalars().all()
        return [
            self._build_candle_from_row(row)
            for row in result
        ]
