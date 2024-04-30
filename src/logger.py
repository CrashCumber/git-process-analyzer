import logging

logging.basicConfig(
    level=logging.WARNING,
    filename="extraction.log",
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger()
