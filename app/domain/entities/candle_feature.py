from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field

TimestampMs = Annotated[str, Field(pattern=r"^\d{13}$")]
Symbol = Annotated[str, Field(min_length=1, max_length=20)]
Timeframe = Annotated[str, Field(
    pattern=r"^(1m|3m|5m|15m|30m|1h|2h|4h|6h|8h|12h|1d)$", max_length=10)]

Price = Annotated[float, Field(gt=0, allow_inf_nan=False, strict=True)]
Volume = Annotated[float, Field(ge=0, allow_inf_nan=False, strict=True)]
Metric = Annotated[float, Field(allow_inf_nan=False, strict=True)]


class CandleFeature(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    timestamp: TimestampMs
    symbol: Symbol
    timeframe: Timeframe

    open: Price
    high: Price
    low: Price
    close: Price
    volume: Volume

    ema20: Metric | None = None
    ema50: Metric | None = None
    ema200: Metric | None = None
    rsi: Metric | None = Field(default=None, ge=0, le=100)
    macd: Metric | None = None
    atr: Metric | None = Field(default=None, ge=0)
    adx: Metric | None = Field(default=None, ge=0, le=100)
    returns: Metric | None = None
