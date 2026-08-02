from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class CandleRow(Base):
    __tablename__ = "candles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)

    open: Mapped[Decimal] = mapped_column(Numeric(precision=20, scale=10), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(precision=20, scale=10), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(precision=20, scale=10), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(precision=20, scale=10), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(precision=30, scale=10), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    open_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "timeframe", "open_time", name="uq_candle_identity"),
        Index("idx_symbol_timeframe_open_time", "symbol", "timeframe", "open_time"),
    )