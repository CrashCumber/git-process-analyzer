import os

from github import Auth, Github

from parsers import CaseIdType, extract_pull_request
from writer import write_dataset


def extract_pull_requests_by_commits_dataset(repo_name: str):
    g = Github(auth=Auth.Token(os.getenv("git_token", "")))

    repo = g.get_repo(repo_name)
    branches = repo.get_branches()

    commits = []

    for branch in branches:
        for commit in repo.get_commits(sha=branch.name):
            if commit.sha in commits:
                continue

            for pull in commit.get_pulls():
                commits.append({"commit.sha": commit.sha, **extract_pull_request(pull)})
    g.close()

    fieldnames = [
        "commit.sha",
        "pull_request.assignees",
        "pull_request.created_at",
        "pull_request.closed_at",
        "pull_request.merged_at",
        "pull_request.comments_numbers",
        "pull_request.comments",
        "pull_request.merged",
        "pull_request.number",
        "pull_request.id",
        "pull_request.user",
        "pull_request.merged_by",
        "pull_request.labels",
        "pull_request.changed_files",
        "pull_request.commits",
        "pull_request.draft",
        "pull_request.milestone",
        "pull_request.state",
        "pull_request.title",
        "pull_request.issue_url",
        "pull_request.head.ref",
        "pull_request.base.ref",
        "pull_request.merge_commit_sha",
        "pull_request.body",
        "pull_request.requested_review",
        "pull_request.review_comments_number",
        "pull_request.review_comments",
        "pull_request.reviews",
        "pull_request.files",
    ]
    write_dataset(commits, fieldnames, CaseIdType.pull_commit.value, repo_name)
