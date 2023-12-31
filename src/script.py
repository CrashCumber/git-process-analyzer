import csv
import logging
import os
import time
from pathlib import Path
from typing import Optional

from github import Auth, Github
from github.Commit import Commit
from github.CommitComment import CommitComment
from github.File import File
from github.GitCommit import GitCommit
from github.Label import Label
from github.NamedUser import NamedUser
from github.PullRequest import PullRequest
from github.PullRequestComment import PullRequestComment
from github.PullRequestReview import PullRequestReview

logging.basicConfig(
    level=logging.INFO,
    filename="commits_extracts.log",
    format="%(asctime)s %(levelname)s %(message)s",
)


event_types = [
    "created",
    "committed",
    "pull_request_created",
    "commented",
    "review_commented",
    "merged_in_default_branch",
    "tagged",
    "released",
    "reverted",
]
# repo_name = "CrashCumber/test"
repo_name = "gorilla/mux"


def extract_file(file: File) -> dict:
    return {
        "file.sha": file.sha,
        "file.filename": file.filename,
        "file.previous_filename": file.previous_filename,
        "file.last_modified": file.last_modified,
        "file.status": file.status,
        "file.changes": file.changes,
        "file.additions": file.additions,
        "file.deletions": file.deletions,
        "file.blob_url": file.blob_url,
        "file.patch": file.patch,
    }


def extract_user(user: Optional[NamedUser]) -> dict:
    if user is None:
        return {}
    return {
        "user.id": user.id,
        "user.name": user.name,
        "user.email": user.email,
        "user.login": user.login,
        "user.type": user.type,
        "user.role": user.role,
        "user.company": user.company,
    }


def extract_git_commit(commit: GitCommit) -> dict:
    return {
        "gitcommit.sha": commit.sha,
        "gitcommit.message": commit.message,
        "gitcommit.parents": [extract_parent_commit(comm) for comm in commit.parents],
        "gitcommit.author.name": commit.author.name,
        "gitcommit.author.date": commit.author.date,
        "gitcommit.author.email": commit.author.email,
        "gitcommit.committer.name": commit.committer.name,
        "gitcommit.committer.date": commit.committer.date,
        "gitcommit.committer.email": commit.committer.email,
    }


def extract_parent_commit(commit: Commit | GitCommit) -> dict:
    return {"commit.sha": commit.sha}


def extract_commit(commit: Commit) -> dict:
    """
    https://api.github.com/repos/gorilla/mux/commits/e44017df2b8798f6bfff81fff1c0b319c1a54496
    """
    return {
        "commit.sha": commit.sha,
        "commit.author": extract_user(commit.author),
        "commit.committer": extract_user(commit.committer),
        "commit.parents": [extract_parent_commit(comm) for comm in commit.parents],
        "commit.stats.additions": commit.stats.additions,
        "commit.stats.deletions": commit.stats.deletions,
        "commit.stats.total": commit.stats.total,
    }


def extract_pull_request_comment(comment: PullRequestComment) -> dict:
    """
    https://api.github.com/repos/gorilla/mux/pulls/691/comments
    """
    return {
        "comment.created_at": comment.created_at,
        "comment.updated_at": comment.updated_at,
        "comment.body": comment.body,
        "comment.id": comment.id,
        "comment.path": comment.path,
        "comment.commit_id": comment.commit_id,
        "comment.original_commit_id": comment.original_commit_id,
        "comment.diff_hunk": comment.diff_hunk,
        "comment.user": extract_user(comment.user),
    }


def extract_comment(comment: CommitComment) -> dict:
    """
    https://api.github.com/repos/gorilla/mux/comments
    """
    return {
        "comment.created_at": comment.created_at,
        "comment.updated_at": comment.updated_at,
        "comment.body": comment.body,
        "comment.id": comment.id,
        "comment.path": comment.path,
        "comment.commit_id": comment.commit_id,
        "comment.sha": comment.commit_id,
        "comment.user": extract_user(comment.user),
    }


def extract_pull_request_review(review: PullRequestReview) -> dict:
    """
    https://api.github.com/repos/gorilla/mux/pulls/691/reviews
    """
    return {
        "review.submitted_at": review.submitted_at,
        "review.body": review.body,
        "review.id": review.id,
        "review.state": review.state,
        "review.commit_id": review.commit_id,
        "review.user": extract_user(review.user),
    }


def extract_label(label: Label) -> dict:
    return {
        "label.description": label.description,
        "label.name": label.name,
        "label.url": label.url,
        "label.color": label.color,
    }


def extract_pull_request(pull_request: PullRequest) -> dict:
    """
    https://api.github.com/repos/gorilla/mux/pulls/691
    https://api.github.com/repos/gorilla/mux/commits/e44017df2b8798f6bfff81fff1c0b319c1a54496/pulls
    """
    comments = [
        extract_pull_request_comment(comment) for comment in pull_request.get_comments()
    ]
    review_comments = [
        extract_pull_request_comment(comment)
        for comment in pull_request.get_review_comments()
    ]
    reviews = [
        extract_pull_request_review(review) for review in pull_request.get_reviews()
    ]
    labels = [extract_label(label) for label in pull_request.get_labels()]
    requested_review = [extract_user(user) for user in pull_request.requested_reviewers]
    assignees = [extract_user(user) for user in pull_request.assignees]
    files = [extract_file(file) for file in pull_request.get_files()]
    return {
        "pull_request.assignees": assignees,
        "pull_request.created_at": pull_request.created_at,
        "pull_request.closed_at": pull_request.closed_at,
        "pull_request.merged_at": pull_request.merged_at,
        "pull_request.comments_numbers": pull_request.comments,
        "pull_request.comments": comments,
        "pull_request.merged": pull_request.merged,
        "pull_request.number": pull_request.number,
        "pull_request.id": pull_request.id,
        "pull_request.user": extract_user(pull_request.user),
        "pull_request.merged_by": extract_user(pull_request.merged_by),
        "pull_request.labels": labels,
        "pull_request.changed_files": pull_request.changed_files,
        "pull_request.commits": pull_request.commits,
        "pull_request.draft": pull_request.draft,
        "pull_request.milestone": pull_request.milestone,
        "pull_request.state": pull_request.state,
        "pull_request.title": pull_request.title,
        "pull_request.issue_url": pull_request.issue_url,
        "pull_request.head.ref": pull_request.head.ref,
        "pull_request.base.ref": pull_request.base.ref,
        "pull_request.merge_commit_sha": pull_request.merge_commit_sha,
        "pull_request.body": pull_request.body,
        "pull_request.requested_review": requested_review,
        "pull_request.review_comments_number": pull_request.review_comments,
        "pull_request.review_comments": review_comments,
        "pull_request.reviews": reviews,
        "pull_request.files": files,
    }


def write_dataset(repo_name: str, commits: dict):
    dir_dataset = Path().absolute() / "datasets" / repo_name
    dir_dataset.mkdir(exist_ok=True, parents=True)
    logging.info("Write dataset in directory %s", dir_dataset)

    with open(
        f"{dir_dataset}/commits{int(time.time())}.csv", "w", newline=""
    ) as file_dataset:
        fieldnames = [
            "commit.sha",
            "gitcommit.sha",
            "commit.message",
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
        writer = csv.DictWriter(file_dataset, fieldnames=fieldnames)
        writer.writeheader()
        for commit in commits.values():
            writer.writerow(commit)


def make_commit_dataset():
    logging.info("Start extract data from %s", repo_name)
    g = Github(auth=Auth.Token(os.getenv("git_token", "")))

    repo = g.get_repo(repo_name)
    branches = repo.get_branches()
    tags = repo.get_tags()
    tag_release_map = {}

    commits = {}

    process_branches = 0
    process_branches_commits = 0
    process_branches_commits_twice = 0
    for branch in branches:
        process_branches += 1
        for commit in repo.get_commits(sha=branch.name):
            process_branches_commits += 1
            if commit.sha in commits:
                process_branches_commits_twice += 1
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

    logging.info("Processed branches %d", process_branches)
    logging.info(
        "Processed branches commits %d, some times %d",
        process_branches_commits,
        process_branches_commits_twice,
    )

    process_tags = 0
    process_tags_commits = 0
    process_tags_commits_twice = 0
    for tag in tags:
        process_tags += 1
        if tag.name not in tag_release_map:
            tag_release_map[tag.name] = repo.get_release(tag.name)

        for commit in repo.get_commits(sha=tag.name):
            process_tags_commits += 1
            if commit.sha in commits:
                process_tags_commits_twice += 1
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
    logging.info("Processed tags %d", process_tags)
    logging.info(
        "Processed tags commits %d, some times %d",
        process_tags_commits,
        process_tags_commits_twice,
    )

    write_dataset(repo_name, commits)
    g.close()


make_commit_dataset()


# assignees = repo.get_assignees()
# watchers = repo.get_watchers()
# collaborators = repo.get_collaborators()
# contributors = repo.get_contributors()
# topics = repo.get_topics()

## rewrite on numpy pandas
## extract by domain model
## mak 4real dataset
## patch lib
