import os

from github import Auth, Github

from logger import logger
from parsers import extract_file
from writer import write_dataset


def extract_files_by_commits_dataset(repo_name: str):
    logger.info("Start extract files by commit from %s", repo_name)

    g = Github(auth=Auth.Token(os.getenv("git_token", "")))
    repo = g.get_repo(repo_name)

    commits = []
    for branch in repo.get_branches():
        for commit in repo.get_commits(sha=branch.name):
            if commit.sha in commits:
                continue

            for file in commit.files:
                commits.append({"commit.sha": commit.sha, **extract_file(file)})

    g.close()
    fieldnames = [
        "commit.sha",
        "file.sha",
        "file.filename",
        "file.previous_filename",
        "file.last_modified",
        "file.status",
        "file.changes",
        "file.additions",
        "file.deletions",
        "file.blob_url",
        "file.patch",
    ]
    write_dataset(commits, fieldnames, "files_by_commit", repo_name)
