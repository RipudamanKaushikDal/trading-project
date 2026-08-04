from abc import ABC, abstractmethod

from typing import Iterable, Optional
from domain.services.logging_service import AppLogger
from domain.entities.candle_feature import CandleFeature
from domain.entities.signals import Signal


class TradingStrategy(ABC):
    """
    Abstract base class for trading strategies.
    """

    def __init__(self, logger: Optional[AppLogger] = None):
        self.logger = logger or AppLogger(None)

    @abstractmethod
    def generate_signals(self, market_data: Iterable[CandleFeature]) -> Signal:
        """
        Generate trading signals based on market data.

        :param market_data: The market data to analyze.
        :return: A list of trading signals.
        """
        pass

    @abstractmethod
    def execute_trade(self, signal: Signal) -> None:
        """
        Execute a trade based on the given signal.

        :param signal: The trading signal to act upon.
        :return: The result of the trade execution.
        """
        pass
