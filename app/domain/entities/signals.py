from enum import StrEnum


class Signal(StrEnum):
    """Enum representing different types of signals."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
