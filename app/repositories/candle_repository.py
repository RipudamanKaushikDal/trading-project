from datetime import UTC, datetime
from decimal import Decimal
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.entities import Candle
from models.candles import CandleRow

class CandleRepository:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _parse_open_time(timestamp_ms: str) -> datetime:
        ms = int(timestamp_ms)
        return datetime.fromtimestamp(ms / 1000, tz=UTC)
      
    def _get_candle_row(self, symbol: str, timeframe: str, open_time:str) -> CandleRow | None:
        open_time_dt = self._parse_open_time(open_time)
        stmt = (
            select(CandleRow)
            .where(
                CandleRow.symbol == symbol,
                CandleRow.timeframe == timeframe,
                CandleRow.open_time == open_time_dt,
            )
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        return result
    
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

    def upsert_many(self, candles: Iterable[Candle], timeframe:str) -> None:
        for candle in candles:
            existing_row = self._get_candle_row(candle.symbol, timeframe, candle.timestamp)
            if existing_row:
                # Update the existing row
                existing_row.open = Decimal(candle.open)
                existing_row.high = Decimal(candle.high)
                existing_row.low = Decimal(candle.low)
                existing_row.close = Decimal(candle.close)
                existing_row.volume = Decimal(candle.volume)
            else:
                # Insert a new row
                new_row = CandleRow(
                    symbol=candle.symbol,
                    timeframe=timeframe,
                    open=Decimal(candle.open),
                    high=Decimal(candle.high),
                    low=Decimal(candle.low),
                    close=Decimal(candle.close),
                    volume=Decimal(candle.volume),
                    open_time=self._parse_open_time(candle.timestamp),
                )
                self.session.add(new_row)
        self.session.commit()

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