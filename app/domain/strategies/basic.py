import logging
from typing import Iterable, Optional
from domain.entities.candle_feature import CandleFeature
from domain.entities.signals import Signal
from domain.strategies.base import TradingStrategy
from domain.services.logging_service import AppLogger


class BasicStrategy(TradingStrategy):
    """Simple EMA/RSI-based strategy."""

    def __init__(self, logger: Optional[AppLogger] = None):
        self.logger = logger or AppLogger(None)

    def generate_signals(self, market_data: Iterable[CandleFeature]) -> Signal:
        candles = list(market_data)
        if not candles:
            self.logger.info("Hold signal generated: no market data available")
            return Signal.HOLD

        latest = candles[-1]
        ema20 = latest.ema20
        ema50 = latest.ema50
        rsi = latest.rsi

        buy_condition = (
            ema20 is not None
            and ema50 is not None
            and rsi is not None
            and ema20 > ema50
            and rsi > 55
        )

        sell_condition = (
            (ema20 is not None and ema50 is not None and ema20 < ema50)
            or (rsi is not None and rsi < 45)
        )

        if buy_condition:
            self.logger.info(
                f"Buy signal generated | ema20={ema20} | ema50={ema50} | rsi={rsi}")

            return Signal.BUY
        elif sell_condition:
            self.logger.info(
                f"Sell signal generated | ema20={ema20} | ema50={ema50} | rsi={rsi}"
            )
            return Signal.SELL
        else:
            self.logger.info(
                f"Hold signal generated | ema20={ema20} | ema50={ema50} | rsi={rsi}"
            )
            return Signal.HOLD

    def execute_trade(self, signal: Signal) -> None:
        """Placeholder for future trade execution logic."""
        pass
