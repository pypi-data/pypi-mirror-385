import logging


def set_logger(level: int = logging.INFO) -> None:
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=level,
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
