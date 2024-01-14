from extract_files import extract_files_by_commits_dataset
from extract_pull_requests import extract_pull_requests_by_commits_dataset
from extract_users import extract_users_by_commits_dataset
from logger import logger

repo_name = "CrashCumber/audio_vizual_information"

logger.info("Start extract case_id=(file, commit) from %s", repo_name)
extract_files_by_commits_dataset(repo_name)
logger.info("Finish extract case_id=(file, commit) from %s", repo_name)

logger.info("Start extract case_id=(pull_request, commit) from %s", repo_name)
extract_pull_requests_by_commits_dataset(repo_name)
logger.info("Finish extract case_id=(pull_request, commit) from %s", repo_name)

logger.info("Start extract case_id=(user, commit) from %s", repo_name)
extract_users_by_commits_dataset(repo_name)
logger.info("Finish extract case_id=(user, commit) from %s", repo_name)
