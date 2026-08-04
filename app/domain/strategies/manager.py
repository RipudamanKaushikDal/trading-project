from domain.entities.candle_feature import CandleFeature
from typing import Iterable
from domain.entities.signals import Signal
from domain.strategies.basic import BasicStrategy


class StrategyManager:
    """Holds a strategy and lets you swap it at runtime."""

    def __init__(self):
        self._strategy = BasicStrategy()  # Default strategy

    def set_strategy(self, strategy):
        """Set a new strategy."""
        self._strategy = strategy

    def get_strategy(self):
        """Get the current strategy."""
        return self._strategy

    def generate_signals(self, market_data: Iterable[CandleFeature]):
        """Generate signals using the current strategy."""
        return self._strategy.generate_signals(market_data)

    def execute_trade(self, signal: Signal):
        """Execute the current strategy."""
        return self._strategy.execute_trade(signal)
