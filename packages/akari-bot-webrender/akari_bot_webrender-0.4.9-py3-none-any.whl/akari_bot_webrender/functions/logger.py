import sys
import traceback
from pathlib import Path
from typing import Optional

from loguru import logger


def basic_logger_format():
    return (
        "<cyan>[WebRender]</cyan>"
        "<yellow>[{name}:{function}:{line}]</yellow>"
        "<green>[{time:YYYY-MM-DD HH:mm:ss}]</green>"
        "<level>[{level}]:{message}</level>"
    )


class LoggingLogger:
    def __init__(self, debug: bool = False, logs_path: str | Path = None):
        try:
            logger.remove(0)
        except ValueError:
            # 如果没有默认的日志处理器，则忽略此错误
            pass

        self.log = logger.bind(name="WebRender")
        self.trace = self.log.trace
        self.debug = self.log.debug
        self.info = self.log.info
        self.success = self.log.success
        self.warning = self.log.warning
        self.error = self.log.error
        self.critical = self.log.critical
        self.debug_flag = debug
        self.log_path = logs_path

        self.log.add(
            sys.stderr,
            format=basic_logger_format(),
            level="DEBUG" if debug else "INFO",
            colorize=True,
            filter=lambda record: record["extra"].get("name") == "WebRender",
        )

        if logs_path:
            self.log.add(
                sink=Path(self.log_path) / "WebRender_debug_{time:YYYY-MM-DD}.log",
                format=basic_logger_format(),
                rotation="00:00",
                retention="1 day",
                level="DEBUG",
                filter=lambda record: record["level"].name == "DEBUG" and record["extra"].get(
                    "name") == "WebRender",
                encoding="utf8",
            )
            self.log.add(
                sink=Path(self.log_path) / "WebRender_{time:YYYY-MM-DD}.log",
                format=basic_logger_format(),
                rotation="00:00",
                retention="10 days",
                level="INFO",
                encoding="utf8",
                filter=lambda record: record["extra"].get(
                    "name") == "WebRender",
            )
        if debug:
            self.log.debug("Debug mode is enabled.")

    def exception(self, message: Optional[str] = None):
        if message:
            self.error(f"{message}\n{traceback.format_exc()}")
        else:
            self.error(traceback.format_exc())
