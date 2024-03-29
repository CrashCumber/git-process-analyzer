import argparse

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
parser.add_argument("--tags", "-t", dest="tags", type=int, default=None, help="number of tags for extractions")
parser.add_argument("--branch", "-b", dest="branch", type=str, default=None, help="branch for extraction")
parser.add_argument("--all-branch", "-ab", dest="all_branch", type=bool, default=True, help="extract all branch")
parser.add_argument("--dir-dataset", "-dp", dest="dir_dataset", default=None, help="folder for dataset")

if __name__ == "__main__":
    args = parser.parse_args()
    logger.info("Start extract from %s", args)
    repo_name = args.author + "/" + args.repo
    extract_commits(
        repo_name,
        branch=args.branch,
        all_branch=args.all_branch,
        commits_cnt=args.commits,
        tag_cnt=args.tags,
        dir_dataset=args.dest_path,
    )
    logger.info("Finish extract from %s", args)
