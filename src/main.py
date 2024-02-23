import argparse

from extract_commit_model import extract_commits
from logger import logger

parser = argparse.ArgumentParser(description="Extract dataset for commit model")
parser.add_argument("--repo", "-r", dest="repo", required=True, help="name of github repository")
parser.add_argument("--author", "-a", dest="author", required=True, help="name of repository`s author or organization")
parser.add_argument("--commits", "-c", dest="commits", type=int, help="number of commits for extractions")
parser.add_argument("--tags", "-t", dest="tags", type=int, help="number of tags for extractions")

if __name__ == "__main__":
    args = parser.parse_args()
    logger.info("Start extract from %s", args)
    repo_name = args.author + "/" + args.repo
    extract_commits(repo_name, commits_cnt=args.commits, tag_cnt=args.tags)
    logger.info("Finish extract from %s", args)
