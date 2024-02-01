import enum
from typing import Optional

from github.Commit import Commit
from github.CommitComment import CommitComment
from github.File import File
from github.GitAuthor import GitAuthor
from github.GitCommit import GitCommit
from github.Label import Label
from github.NamedUser import NamedUser
from github.PullRequest import PullRequest
from github.PullRequestComment import PullRequestComment
from github.PullRequestReview import PullRequestReview


class CaseIdType(enum.StrEnum):
    user_commit = "user_commit"
    pull_commit = "pull_request_commit"
    file_commit = "file_commit"


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


def extract_user(user: Optional[NamedUser] | Optional[GitAuthor]) -> dict:
    if user is None:
        return {}

    if isinstance(user, GitAuthor):
        return {
            "user.name": user.name,
            "user.email": user.email,
            "user.date": user.date,
        }

    return {
        "user.id": user.id,
        "user.name": user.name,
        # "user.email": user.email,
        "user.login": user.login,
        "user.type": user.type,
        "user.role": user.role,
        "user.company": user.company,
    }


def extract_author(commit: Commit) -> dict:
    if commit.author is None or commit.commit.author is None:
        return {}
    return {
        "user.id": commit.author.id,
        "user.type": commit.author.type,
        "user.name": commit.commit.author.name,
        "user.date": commit.commit.author.date,
    }


def extract_base_user(user: Optional[NamedUser], git_user: Optional[GitAuthor]) -> dict:
    data = {}
    if user is not None:
        data["user.id"] = user.id
        data["user.type"] = user.type

    if git_user is not None:
        data["user.name"] = git_user.name
        data["user.date"] = git_user.date
    return data


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
