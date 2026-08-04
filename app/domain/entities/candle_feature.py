from pydantic import BaseModel


class CandleFeature(BaseModel):
    timestamp: str
    symbol: str
    timeframe: str

    open: float
    high: float
    low: float
    close: float
    volume: float

    ema20: float | None = None
    ema50: float | None = None
    ema200: float | None = None
    rsi: float | None = None
    macd: float | None = None
    atr: float | None = None
    adx: float | None = None
    returns: float | None = None
