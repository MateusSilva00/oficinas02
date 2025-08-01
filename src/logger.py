from loguru import logger

logger.add(
    "logs/debug.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    level="DEBUG",
    rotation="1 MB",
    retention="10 days",
)
