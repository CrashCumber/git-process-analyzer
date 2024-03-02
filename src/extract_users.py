import enum
import os
from typing import Optional

from attrs import define, field
from github import Auth, Github
from github.Commit import Commit
from github.GitAuthor import GitAuthor
from github.NamedUser import NamedUser
from github.PullRequest import PullRequest
from github.Repository import Repository

from logger import logger
from parsers import CaseIdType
from writer import prepare_file


class Counter:
    def __init__(self):
        self._count = -1

    def __call__(self):
        self._count += 1
        return self._count

    @property
    def count(self):
        return self._count


counter = Counter()


class UserEventType(enum.StrEnum):
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


@define()
class Row:
    commit_sha: str = field()
    event_type: str = field()
    datetime: str = field()
    user_id: str = field()
    user_login: str = field()
    commit_stats_additions: int = field()
    commit_stats_deletions: int = field()
    commit_stats_total: int = field()
    commit_message: int = field()


def extract_commit(commit: Commit) -> dict:
    if commit.stats is None:
        return {}
    return {
        "commit.stats.additions": commit.stats.additions,
        "commit.stats.deletions": commit.stats.deletions,
        "commit.stats.total": commit.stats.total,
        "commit.commit.message": commit.commit.message,
    }


def extract_user(
    user: Optional[NamedUser], git_user: Optional[GitAuthor] = None
) -> dict:
    data = {}
    if user is not None:
        data["user.id"] = user.id
        data["user.login"] = user.login

    if git_user is not None:
        data["user.name"] = git_user.name
    return data


def row(commit, event, datetime, user):
    return {
        "commit.sha": commit.sha,
        "event_type": event,
        "datetime": datetime,
        **extract_user(user),
        **extract_commit(commit),
    }


def extract_pull_request(repo: Repository, pull: PullRequest, writer):
    commits = pull.get_commits()

    for commit in commits:
        for user in pull.assignees:
            counter()
            writer.writerow(
                {
                    "commit.sha": commit.sha,
                    "event_type": UserEventType.is_assigned_pull_request_to.value,
                    "datetime": pull.created_at,
                    **extract_user(user),
                    **extract_commit(commit),
                }
            )
        for user in pull.requested_reviewers:
            counter()
            writer.writerow(
                {
                    "commit.sha": commit.sha,
                    "event_type": UserEventType.is_requested_review_pull_request_from.value,
                    "datetime": pull.created_at,
                    **extract_user(user),
                    **extract_commit(commit),
                }
            )
        counter()
        writer.writerow(
            {
                "commit.sha": commit.sha,
                "event_type": UserEventType.merge_pull_request.value,
                "datetime": pull.merged_at,
                **extract_user(pull.merged_by),
                **extract_commit(commit),
            }
        )
        counter()
        writer.writerow(
            {
                "commit.sha": commit.sha,
                "event_type": UserEventType.create_pull_request.value,
                "datetime": pull.created_at,
                **extract_user(pull.user),
                **extract_commit(commit),
            }
        )

    merge_commit = repo.get_commit(pull.merge_commit_sha)
    counter()
    writer.writerow(
        {
            "commit.sha": merge_commit.sha,
            "event_type": UserEventType.merge_pull_request.value,
            "datetime": pull.merged_at,
            **extract_user(pull.merged_by),
            **extract_commit(merge_commit),
        }
    )

    for comment in pull.get_comments():
        counter()
        commit = repo.get_commit(comment.commit_id)
        writer.writerow(
            {
                "commit.sha": commit.sha,
                "event_type": UserEventType.add_pull_request_comment.value,
                "datetime": comment.created_at,
                **extract_user(comment.user),
                **extract_commit(commit),
            }
        )

    for comment in pull.get_reviews():
        counter()
        commit = repo.get_commit(comment.commit_id)
        writer.writerow(
            {
                "commit.sha": commit.sha,
                "event_type": UserEventType.add_pull_request_review.value,
                "datetime": comment.submitted_at,
                **extract_user(comment.user),
                **extract_commit(commit),
            }
        )


def extract_users_by_commits_dataset(repo_name: str, number=None):
    fieldnames = [
        "commit.sha",
        "event_type",
        "datetime",
        "user.id",
        "user.login",
        "user.type",
        "commit.stats.additions",
        "commit.stats.deletions",
        "commit.stats.total",
        "commit.commit.message",
    ]
    file, writer = prepare_file(fieldnames, CaseIdType.user_commit.value, repo_name)
    commits_parsed = set()
    pulls_parsed = set()

    g = Github(auth=Auth.Token(os.getenv("git_token", "")))
    try:
        repo = g.get_repo(repo_name)

        branches = repo.get_branches()

        for branch in branches:
            for commit in repo.get_commits(sha=branch.name):
                if commit.sha in commits_parsed:
                    continue
                if number is not None and counter.count >= number:
                    break

                counter()
                commits_parsed.add(commit.sha)
                writer.writerow(
                    {
                        "commit.sha": commit.sha,
                        "event_type": UserEventType.create_commit.value,
                        "datetime": commit.commit.author.date,
                        **extract_user(commit.author),
                        **extract_commit(commit),
                    }
                )
                writer.writerow(
                    {
                        "commit.sha": commit.sha,
                        "event_type": UserEventType.commit_commit.value,
                        "datetime": commit.commit.committer.date,
                        **extract_user(commit.committer),
                        **extract_commit(commit),
                    }
                )

                for pull in commit.get_pulls():
                    if pull.id not in pulls_parsed:
                        extract_pull_request(repo, pull, writer)
                        pulls_parsed.add(pull.id)

        tags = repo.get_tags()
        for tag in tags:
            counter()
            if number is not None and counter.count >= number:
                break
            release = repo.get_release(tag.name)
            writer.writerow(
                {
                    "commit.sha": tag.commit.sha,
                    "event_type": UserEventType.create_release.value,
                    "datetime": release.created_at,
                    **extract_user(release.author),
                    **extract_commit(tag.commit),
                }
            )
            writer.writerow(
                {
                    "commit.sha": tag.commit.sha,
                    "event_type": UserEventType.publish_release.value,
                    "datetime": release.published_at,
                    **extract_user(release.author),
                    **extract_commit(tag.commit),
                }
            )
        logger.info("SUCCESS")
    except Exception as e:
        logger.exception(e)
        logger.error("FAIL")

    g.close()
    file.close()
    logger.info(commits_parsed)
