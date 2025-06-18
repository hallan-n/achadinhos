import sys

from loguru import logger

logger.remove()

logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level:<8}</level> | "
        "<magenta>{file}</magenta>:<yellow>{line}</yellow> | "
        "<level>{message}</level>"
    ),
    level="INFO",
)
