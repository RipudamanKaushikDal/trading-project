from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

TimestampMs = Annotated[str, Field(pattern=r"^\d{13}$")]
Symbol = Annotated[str, Field(min_length=1, max_length=20)]
Price = Annotated[float, Field(gt=0, allow_inf_nan=False, strict=True)]
Volume = Annotated[float, Field(ge=0, allow_inf_nan=False, strict=True)]


class Candle(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    timestamp: TimestampMs
    symbol: Symbol
    open: Price
    high: Price
    low: Price
    close: Price
    volume: Volume
