import enum
import os

from github import Auth, Github
from github.PullRequest import PullRequest

from parsers import CaseIdType, extract_user
from writer import write_dataset


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


def parse_pull_request_row(pull: PullRequest, rows: list):
    commits = pull.get_commits()

    for commit in commits:
        for user in pull.assignees:
            rows.append(
                {
                    "commit.sha": commit.sha,
                    "event_type": UserEventType.is_assigned_pull_request_to.value,
                    **extract_user(user),
                }
            )
        for user in pull.requested_reviewers:
            rows.append(
                {
                    "commit.sha": commit.sha,
                    "event_type": UserEventType.is_requested_review_pull_request_from.value,
                    **extract_user(user),
                }
            )
        rows.append(
            {
                "commit.sha": commit.sha,
                "event_type": UserEventType.merge_pull_request.value,
                "datetime": pull.merged_at,
                **extract_user(pull.merged_by),
            }
        )
        rows.append(
            {
                "commit.sha": commit.sha,
                "event_type": UserEventType.create_pull_request.value,
                "datetime": pull.created_at,
                **extract_user(pull.user),
            }
        )

    rows.append(
        {
            "commit.sha": pull.merge_commit_sha,
            "event_type": UserEventType.merge_pull_request.value,
            "datetime": pull.merged_at,
            **extract_user(pull.merged_by),
        }
    )
    for comment in pull.get_comments():
        rows.append(
            {
                "commit.sha": comment.commit_id,
                "event_type": UserEventType.add_pull_request_comment.value,
                "datetime": comment.created_at,
                **extract_user(comment.user),
            }
        )

    for comment in pull.get_reviews():
        rows.append(
            {
                "commit.sha": comment.commit_id,
                "event_type": UserEventType.add_pull_request_review.value,
                "datetime": comment.submitted_at,
                **extract_user(comment.user),
            }
        )


# add releases author, requested_teams
def extract_users_by_commits_dataset(repo_name: str):
    g = Github(auth=Auth.Token(os.getenv("git_token", "")))
    repo = g.get_repo(repo_name)

    rows = []

    branches = repo.get_branches()
    commits_parsed = set()
    pulls_parsed = set()

    for branch in branches:
        for commit in repo.get_commits(sha=branch.name):
            for pull in commit.get_pulls():
                if pull.id not in pulls_parsed:
                    parse_pull_request_row(pull, rows)
                    pulls_parsed.add(pull.id)

            if commit.sha in commits_parsed:
                continue

            commits_parsed.add(commit.sha)
            rows.append(
                {
                    "commit.sha": commit.sha,
                    "event_type": UserEventType.create_commit.value,
                    "datetime": commit.commit.author.date,
                    **extract_user(commit.author),
                }
            )
            rows.append(
                {
                    "commit.sha": commit.sha,
                    "event_type": UserEventType.commit_commit.value,
                    "datetime": commit.commit.committer.date,
                    **extract_user(commit.committer),
                }
            )

    tags = repo.get_tags()
    for tag in tags:
        release = repo.get_release(tag.name)
        rows.append(
            {
                "commit.sha": tag.commit.sha,
                "event_type": UserEventType.create_release.value,
                "datetime": release.created_at,
                **extract_user(release.author),
            }
        )
        rows.append(
            {
                "commit.sha": tag.commit.sha,
                "event_type": UserEventType.publish_release.value,
                "datetime": release.published_at,
                **extract_user(release.author),
            }
        )

    g.close()
    fieldnames = [
        "commit.sha",
        "event_type",
        "datetime",
        "user.id",
        "user.login",
        "user.name",
        "user.email",
        "user.type",
        "user.role",
        "user.company",
    ]
    write_dataset(rows, fieldnames, CaseIdType.user_commit.value, repo_name)
