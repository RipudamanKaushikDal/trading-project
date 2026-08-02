from enum import IntEnum


class TIMEFRAME(IntEnum):
    MIN_1 = 60_000
    MIN_3 = 180_000
    MIN_5 = 300_000
    MIN_15 = 900_000
    MIN_30 = 1_800_000
    HOUR_1 = 3_600_000
    HOUR_2 = 7_200_000
    HOUR_4 = 14_400_000
    HOUR_6 = 21_600_000
    HOUR_8 = 28_800_000
    HOUR_12 = 43_200_000
    DAY_1 = 86_400_000

    @property
    def ccxt_value(self) -> str:
        mapping = {
            TIMEFRAME.MIN_1: "1m",
            TIMEFRAME.MIN_3: "3m",
            TIMEFRAME.MIN_5: "5m",
            TIMEFRAME.MIN_15: "15m",
            TIMEFRAME.MIN_30: "30m",
            TIMEFRAME.HOUR_1: "1h",
            TIMEFRAME.HOUR_2: "2h",
            TIMEFRAME.HOUR_4: "4h",
            TIMEFRAME.HOUR_6: "6h",
            TIMEFRAME.HOUR_8: "8h",
            TIMEFRAME.HOUR_12: "12h",
            TIMEFRAME.DAY_1: "1d",
        }
        return mapping[self]
