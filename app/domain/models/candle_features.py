from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from domain.models.base import Base


class CandleFeatureRow(Base):
    __tablename__ = "candle_features"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(10), nullable=False)
    open_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    open: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=10), nullable=False)
    high: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=10), nullable=False)
    low: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=10), nullable=False)
    close: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=10), nullable=False)
    volume: Mapped[Decimal] = mapped_column(
        Numeric(precision=30, scale=10), nullable=False)

    ema20: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=10), nullable=True)
    ema50: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=10), nullable=True)
    ema200: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=10), nullable=True)
    rsi: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=10), nullable=True)
    macd: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=10), nullable=True)
    atr: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=10), nullable=True)
    adx: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=10), nullable=True)
    returns: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=10), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("symbol", "timeframe", "open_time",
                         name="uq_feature_identity"),
        Index("idx_feature_symbol_timeframe_open_time",
              "symbol", "timeframe", "open_time"),
    )
