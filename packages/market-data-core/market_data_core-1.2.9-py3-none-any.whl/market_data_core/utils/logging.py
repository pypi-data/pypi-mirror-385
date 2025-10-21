from loguru import logger

logger.add(
    "logs/market-data-core.log", rotation="10 MB", enqueue=True, backtrace=True, diagnose=False
)
