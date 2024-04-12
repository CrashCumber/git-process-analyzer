import logging

logging.basicConfig(
    level=logging.INFO,
    filename="extraction.log",
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger()
