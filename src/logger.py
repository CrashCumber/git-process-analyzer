import logging

logging.basicConfig(
    level=logging.INFO,
    filename="commits_extracts.log",
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger()
