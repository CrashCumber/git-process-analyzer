from extract_files import extract_files_by_commits_dataset
from extract_pull_requests import extract_pull_requests_by_commits_dataset
from extract_users import extract_users_by_commits_dataset
from logger import logger

repo_name = "gorilla/mux"

logger.info("Start extract case_id=(user, commit) from %s", repo_name)
extract_users_by_commits_dataset(repo_name, 30)
logger.info("Finish extract case_id=(user, commit) from %s", repo_name)
