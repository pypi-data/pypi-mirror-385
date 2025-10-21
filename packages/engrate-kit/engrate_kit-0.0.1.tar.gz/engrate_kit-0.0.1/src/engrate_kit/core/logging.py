import contextlib
import logging

import structlog

CRITICAL = logging.CRITICAL
DEBUG = logging.DEBUG
ERROR = logging.ERROR
INFO = logging.INFO
WARNING = logging.WARNING


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""

    return structlog.getLogger(name)


def set_level(level: int | str):
    """Sets the global log level."""

    if (isinstance(level, int) and level > 0) or level in logging._nameToLevel:
        logging.getLogger().setLevel(level)
    else:
        logging.getLogger(__name__).warning("Invalid log level %s; ignoring.", level)


def configure_logging(level: str | int | None = None, json_format: bool = False):
    """Initializes the logging system."""

    log_level = getattr(logging, level) if isinstance(level, str) else level

    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_format:
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=shared_processors,
        )
    else:
        formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=True),
            foreign_pre_chain=shared_processors,
        )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level or INFO)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


@contextlib.contextmanager
def level(level: int):
    """Temporarily modifies the log level.

    Usage:
    ```
    with logger.level(logger.DEBUG):
        ...
    ```

    """

    logger = logging.getLogger()
    old_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(old_level)
