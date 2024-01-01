import os

from github import Auth, Github

from logger import logger
from writer import write_dataset


# add releases author
def extract_users_by_commits_dataset(repo_name: str):
    logger.info("Start extract users by commits from %s", repo_name)
    g = Github(auth=Auth.Token(os.getenv("git_token", "")))

    repo = g.get_repo(repo_name)
    branches = repo.get_branches()
    commits = {}

    for branch in branches:
        for commit in repo.get_commits(sha=branch.name):
            if commit.sha in commits:
                continue

            pulls = commit.get_pulls()
            assignees = []
            requested_reviewers = []
            users = []
            commented = []
            merged_by = []
            for pull in pulls:
                for user in pull.assignees:
                    assignees.append(user.name)
                for user in pull.requested_reviewers:
                    requested_reviewers.append(user.name)
                for comment in pull.get_comments():
                    commented.append(comment.user.name)
                users.append(pull.user.name)
                merged_by.append(pull.merged_by.name)

            commits[commit.sha] = {
                "commit.sha": commit.sha,
                "commit.author.name": commit.author.name,
                "commit.committer.name": commit.committer.name,
                "pull_requests.users.name": users,
                "pull_requests.assignees.name": assignees,
                "pull_requests.requested_reviewers.name": requested_reviewers,
                "pull_requests.merged_by.name": [],
                "comments.users.name": [
                    comment.user.name for comment in commit.get_comments()
                ],
            }

    g.close()
    fieldnames = [
        "commit.sha",
        "commit.author.name",
        "commit.committer.name",
        "pull_requests.users.name",
        "pull_requests.assignees.name",
        "pull_requests.requested_reviewers.name",
        "pull_requests.merged_by.name",
        "comments.users.name",
    ]
    write_dataset(commits, fieldnames, "users_by_commits", repo_name)
