import enum
import os

from github import Auth, Github

from parsers import (extract_comment, extract_commit, extract_file,
                     extract_git_commit, extract_pull_request)
from writer import write_dataset


def extract_all_commits_dataset(repo_name: str):
    g = Github(auth=Auth.Token(os.getenv("git_token", "")))

    repo = g.get_repo(repo_name)
    branches = repo.get_branches()
    tags = repo.get_tags()
    tag_release_map = {}

    commits = {}

    for branch in branches:
        for commit in repo.get_commits(sha=branch.name):
            if commit.sha in commits:
                commits[commit.sha]["commit.branches"].append(branch.name)
                continue

            files = [extract_file(file) for file in commit.files]
            pull_requests = [extract_pull_request(pull) for pull in commit.get_pulls()]
            comments = [extract_comment(comment) for comment in commit.get_comments()]
            commits[commit.sha] = {
                **extract_git_commit(commit.commit),
                **extract_commit(commit),
                "commit.branches": [branch.name],
                "commit.tags": [],
                "commit.release": [],
                "commit.pull_requests": pull_requests,
                "commit.files": files,
                "commit.comments": comments,
            }
    for tag in tags:
        if tag.name not in tag_release_map:
            tag_release_map[tag.name] = repo.get_release(tag.name)

        for commit in repo.get_commits(sha=tag.name):
            if commit.sha in commits:
                commits[commit.sha]["commit.tags"].append(tag.name)
                # add more info
                commits[commit.sha]["commit.release"] = tag_release_map[tag.name]
                continue

            files = [extract_file(file) for file in commit.files]
            pull_requests = [extract_pull_request(pull) for pull in commit.get_pulls()]
            comments = [extract_comment(comment) for comment in commit.get_comments()]
            commits[commit.sha] = {
                **extract_git_commit(commit.commit),
                **extract_commit(commit),
                "commit.branches": [],
                "commit.release": tag_release_map[tag.name],
                "commit.tags": [tag.name],
                "commit.pull_requests": pull_requests,
                "commit.files": files,
                "commit.comments": comments,
            }

    g.close()
    fieldnames = [
        "commit.sha",
        "gitcommit.sha",
        "gitcommit.message",
        "commit.parents",
        "gitcommit.parents",
        "gitcommit.author.name",
        "gitcommit.author.email",
        "gitcommit.author.date",
        "commit.author",
        "gitcommit.committer.name",
        "gitcommit.committer.email",
        "gitcommit.committer.date",
        "commit.committer",
        "commit.stats.additions",
        "commit.stats.deletions",
        "commit.stats.total",
        "commit.branches",
        "commit.release",
        "commit.tags",
        "commit.pull_requests",
        "commit.files",
        "commit.comments",
    ]
    write_dataset(commits, fieldnames, "unique_commits", repo_name)


class CommitEventType(enum.StrEnum):
    commit_commit = "commit_commit"
    create_commit = "create_commit"
    create_pull_request = "create_pull_request"
    is_assigned_pull_request_to = "is_assigned_pull_request_to"
    is_requested_review_pull_request_from = "requested_review_from"
    merge_pull_request = "merge_pull_request"
    add_pull_request_comment = "add_pull_request_comment"
    add_pull_request_review = "add_pull_request_review"
    create_release = "create_release"
    publish_release = "publish_release"
