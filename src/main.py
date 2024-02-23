from extract_commit_model import extract_commits
from logger import logger

repo_name = "gorilla/mux"

logger.info("Start extract from %s", repo_name)
extract_commits(repo_name, 30)
logger.info("Finish extract from %s", repo_name)
