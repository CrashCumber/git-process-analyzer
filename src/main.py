import argparse
import os

from extract_commit_model import extract_commits
from logger import logger

parser = argparse.ArgumentParser(description="Extract dataset for commit model")
parser.add_argument("--repo", "-r", dest="repo", required=True, help="name of github repository")
parser.add_argument(
    "--author",
    "-a",
    dest="author",
    required=True,
    help="name of repository`s author or organization",
)
parser.add_argument(
    "--commits",
    "-c",
    dest="commits",
    type=int,
    default=None,
    help="number of commits for extractions",
)
parser.add_argument(
    "--tags",
    "-t",
    dest="tags",
    type=int,
    default=None,
    help="number of tags for extractions",
)
parser.add_argument(
    "--branch",
    "-b",
    dest="branch",
    type=str,
    default=None,
    help="branch for extraction",
)
parser.add_argument(
    "--all-branch",
    "-ab",
    dest="all_branch",
    default=False,
    action="store_true",
    help="extract all branch, flag",
)
parser.add_argument("--dir-dataset", "-dp", dest="dir_dataset", default=None, help="folder for dataset")

if __name__ == "__main__":
    args = parser.parse_args()
    logger.warn("Start extract from %s", args)
    repo_name = args.author + "/" + args.repo
    status = extract_commits(
        repo_name,
        branch=args.branch,
        all_branch=args.all_branch,
        commits_cnt=args.commits,
        tag_cnt=args.tags,
        dir_dataset=args.dir_dataset,
    )
    logger.warn("Finish extract from status=%d: %s", status, args)
    os._exit(status)
