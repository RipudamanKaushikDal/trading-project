import logging
import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()


class AppLogger:
    def __init__(self, logger: logging.Logger | None, context: dict[str, Any] | None = None):
        self._logger = logger
        self._context = context or {}
        if self._logger is not None:
            self._logger.setLevel(
                getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
            )

    def child(self, **context: Any) -> "AppLogger":
        merged = dict(self._context)
        merged.update(context)
        return AppLogger(self._logger, merged)

    def _merge(self, extra: dict[str, Any] | None) -> dict[str, Any]:
        merged = dict(self._context)
        if extra:
            merged.update(extra)
        return merged

    def _log(self, level: int, message: str, **extra: Any) -> None:
        if self._logger is None:
            return
        self._logger.log(level, message, extra=self._merge(extra))

    def debug(self, message: str, **extra: Any) -> None:
        self._log(logging.DEBUG, message, **extra)

    def info(self, message: str, **extra: Any) -> None:
        self._log(logging.INFO, message, **extra)

    def warning(self, message: str, **extra: Any) -> None:
        self._log(logging.WARNING, message, **extra)

    def error(self, message: str, **extra: Any) -> None:
        self._log(logging.ERROR, message, **extra)

    def exception(self, message: str, **extra: Any) -> None:
        if self._logger is None:
            return
        self._logger.exception(message, extra=self._merge(extra))
