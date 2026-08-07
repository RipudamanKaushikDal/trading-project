from datetime import UTC, datetime
from decimal import Decimal
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from domain.entities.candle_feature import CandleFeature
from domain.models.candle_features import CandleFeatureRow


class CandleFeatureRepository:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _parse_open_time(timestamp_ms: str) -> datetime:
        return datetime.fromtimestamp(int(timestamp_ms) / 1000, tz=UTC)

    @staticmethod
    def _to_decimal(value: float | None) -> Decimal | None:
        if value is None:
            return None
        return Decimal(str(value))

    def upsert_many(self, features: Iterable[CandleFeature]) -> None:
        rows = [
            {
                "symbol": f.symbol,
                "timeframe": f.timeframe,
                "open_time": self._parse_open_time(f.timestamp),
                "open": Decimal(str(f.open)),
                "high": Decimal(str(f.high)),
                "low": Decimal(str(f.low)),
                "close": Decimal(str(f.close)),
                "volume": Decimal(str(f.volume)),
                "ema20": self._to_decimal(f.ema20),
                "ema50": self._to_decimal(f.ema50),
                "ema200": self._to_decimal(f.ema200),
                "rsi": self._to_decimal(f.rsi),
                "macd": self._to_decimal(f.macd),
                "atr": self._to_decimal(f.atr),
                "adx": self._to_decimal(f.adx),
                "returns": self._to_decimal(f.returns),
                "forward_return_6h": self._to_decimal(f.forward_return_6h),
                "label": f.label.value if f.label is not None else None,
            }
            for f in features
        ]

        if not rows:
            return

        stmt = insert(CandleFeatureRow).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["symbol", "timeframe", "open_time"],
            set_={
                "open": stmt.excluded.open,
                "high": stmt.excluded.high,
                "low": stmt.excluded.low,
                "close": stmt.excluded.close,
                "volume": stmt.excluded.volume,
                "ema20": stmt.excluded.ema20,
                "ema50": stmt.excluded.ema50,
                "ema200": stmt.excluded.ema200,
                "rsi": stmt.excluded.rsi,
                "macd": stmt.excluded.macd,
                "atr": stmt.excluded.atr,
                "adx": stmt.excluded.adx,
                "returns": stmt.excluded.returns,
                "forward_return_6h": stmt.excluded.forward_return_6h,
                "label": stmt.excluded.label,
            },
        )
        self.session.execute(stmt)

    def get_features(self, symbol: str, timeframe: str, start: datetime, end: datetime):
        stmt = (
            select(CandleFeatureRow)
            .where(
                CandleFeatureRow.symbol == symbol,
                CandleFeatureRow.timeframe == timeframe,
                CandleFeatureRow.open_time >= start.replace(tzinfo=UTC),
                CandleFeatureRow.open_time <= end.replace(tzinfo=UTC),
            )
            .order_by(CandleFeatureRow.open_time)
        )
        return self.session.execute(stmt).scalars().all()
