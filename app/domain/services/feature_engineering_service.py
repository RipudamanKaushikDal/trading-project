from datetime import datetime
import pandas as pd
import pandas_ta as ta

from domain.entities.candle_feature import CandleFeature
from domain.repositories.candle_repository import CandleRepository
from domain.repositories.candle_feature_repository import CandleFeatureRepository
from domain.services.logging_service import AppLogger


class CandleFeatureEngineeringService:
    def __init__(
        self,
        candle_repo: CandleRepository,
        feature_repo: CandleFeatureRepository,
        logger: AppLogger | None = None,
    ):
        self.candle_repo = candle_repo
        self.feature_repo = feature_repo
        self.logger = logger or AppLogger(None)

    @staticmethod
    def _nan_to_none(value: float):
        return None if pd.isna(value) else float(value)

    def build_and_store(
        self,
        symbol: str,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
    ) -> int:
        candles = list(self.candle_repo.get_candles(
            symbol, timeframe, start_time, end_time))
        if not candles:
            self.logger.info(
                "No candles found for feature engineering", symbol=symbol, timeframe=timeframe)
            return 0

        df = pd.DataFrame(
            {
                "timestamp": [c.timestamp for c in candles],
                "symbol": [c.symbol for c in candles],
                "open": [c.open for c in candles],
                "high": [c.high for c in candles],
                "low": [c.low for c in candles],
                "close": [c.close for c in candles],
                "volume": [c.volume for c in candles],
            }
        )

        df["open"] = pd.to_numeric(df["open"], errors="coerce")
        df["high"] = pd.to_numeric(df["high"], errors="coerce")
        df["low"] = pd.to_numeric(df["low"], errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
        df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"])

        df["ema20"] = ta.ema(df["close"], length=20)
        df["ema50"] = ta.ema(df["close"], length=50)
        df["ema200"] = ta.ema(df["close"], length=200)
        df["rsi"] = ta.rsi(df["close"], length=14)

        macd_df = ta.macd(df["close"], fast=12, slow=26, signal=9)
        df["macd"] = macd_df["MACD_12_26_9"]

        df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)

        adx_df = ta.adx(df["high"], df["low"], df["close"], length=14)
        df["adx"] = adx_df["ADX_14"]

        df["returns"] = df["close"].pct_change()

        features: list[CandleFeature] = []
        for row in df.itertuples(index=False):
            features.append(
                CandleFeature(
                    timestamp=str(row.timestamp),
                    symbol=row.symbol,
                    timeframe=timeframe,
                    open=float(row.open),
                    high=float(row.high),
                    low=float(row.low),
                    close=float(row.close),
                    volume=float(row.volume),
                    ema20=self._nan_to_none(row.ema20),
                    ema50=self._nan_to_none(row.ema50),
                    ema200=self._nan_to_none(row.ema200),
                    rsi=self._nan_to_none(row.rsi),
                    macd=self._nan_to_none(row.macd),
                    atr=self._nan_to_none(row.atr),
                    adx=self._nan_to_none(row.adx),
                    returns=self._nan_to_none(row.returns),
                )
            )

        self.feature_repo.upsert_many(features)
        self.logger.info("Stored candle features", symbol=symbol,
                         timeframe=timeframe, count=len(features))
        return len(features)

    def get_features(
        self,
        symbol: str,
        timeframe: str,
        start_time: datetime,
        end_time: datetime,
    ) -> list[CandleFeature]:
        return list(self.feature_repo.get_features(symbol, timeframe, start_time, end_time))
