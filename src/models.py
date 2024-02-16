import enum
from typing import Optional

from attrs import define, field
from github.Commit import Commit
from github.File import File
from github.GitAuthor import GitAuthor
from github.NamedUser import NamedUser


class CaseIdType(enum.StrEnum):
    user_commit = "user_commit"
    pull_commit = "pull_request_commit"
    file_commit = "file_commit"
    commits = "commits"


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


@define(kw_only=True, frozen=True, slots=True)
class CommitRow:
    """
    https://api.github.com/repos/gorilla/mux/commits/e44017df2b8798f6bfff81fff1c0b319c1a54496
    """

    sha: str = field()
    message: str = field()
    url: str = field()
    html_url: str = field()
    comments_url: str = field()
    tree_sha: str = field()
    tree_url: str = field()
    stats_additions: int = field(converter=int)
    stats_deletions: int = field(converter=int)
    stats_total: int = field(converter=int)
    author_id: int = field()
    committer_id: int = field()
    create_date: str = field()
    commit_date: str = field()

    @classmethod
    def from_dict(cls, commit: Commit):
        row = {
            "sha": commit.sha,
            "message": commit.commit.message,
            "create_date": commit.commit.author.date,
            "commit_date": commit.commit.committer.date,
            "author_id": commit.author.id,
            "committer_id": commit.committer.id,
            "stats_additions": commit.stats.additions,
            "stats_deletions": commit.stats.deletions,
            "stats_total": commit.stats.total,
            "tree_sha": commit.commit.tree.sha,
            "tree_url": commit.commit.tree.url,
            "comments_url": commit.comments_url,
            "url": commit.url,
            "html_url": commit.html_url,
        }

        return cls(**row)


@define(kw_only=True, frozen=True)
class FileRow:
    """
    https://api.github.com/repos/gorilla/mux/commits/e44017df2b8798f6bfff81fff1c0b319c1a54496
    https://api.github.com/repos/gorilla/mux/contents/regexp.go?ref=e44017df2b8798f6bfff81fff1c0b319c1a54496
    """

    commit_sha: str = field()
    sha: str = field()
    filename: str = field()
    previous_filename: str = field()
    last_modified: str = field()
    status: str = field()
    additions: int = field(converter=int)
    deletions: int = field(converter=int)
    changes: int = field(converter=int)
    patch: str = field()
    content_url: str = field()
    blob_url: str = field()

    @classmethod
    def from_dict(cls, commit_sha: str, file: File):
        row = {
            "commit_sha": commit_sha,
            "sha": file.sha,
            "filename": file.filename,
            "previous_filename": file.previous_filename,
            "last_modified": file.last_modified,
            "status": file.status,
            "changes": file.changes,
            "additions": file.additions,
            "deletions": file.deletions,
            "blob_url": file.blob_url,
            "content_url": file.contents_url,
            "patch": file.patch,
        }
        return cls(**row)


@define(kw_only=True, frozen=True)
class UserRow:
    """https://api.github.com/users/das7pad"""

    commit_sha: str = field()
    role: str = field()
    id: str = field()
    name: str = field()
    login: str = field()
    email: str = field()
    url: str = field()
    actor: str = field()
    date: str = field()
    followers_url: str = field()
    followers: int = field(default=None)
    following_url: str = field()
    following: int = field(default=None)
    subscriptions_url: str = field()
    organizations_url: str = field()
    repos_url: str = field()
    received_events_url: str = field()
    site_admin: bool = field(converter=bool)
    type: str = field()
    company: str = field()

    @classmethod
    def from_dict(cls, commit_sha: str, actor: str, user: NamedUser, git_user: GitAuthor):
        row = {
            "commit_sha": commit_sha,
            "actor": actor,
            "date": git_user.date,
            "id": user.id,
            "url": user.url,
            "name": user.name,
            "email": user.email,
            "login": user.login,
            "type": user.type,
            "role": user.role,
            "company": user.company,
            "followers": user.followers,
            "followers_url": user.followers_url,
            "following": user.following,
            "following_url": user.following_url,
            "subscriptions_url": user.subscriptions_url,
            "organizations_url": user.organizations_url,
            "repos_url": user.repos_url,
            "received_events_url": user.received_events_url,
            "site_admin": user.site_admin,
        }
        return cls(**row)


@define(frozen=True)
class TagRow:
    """https://api.github.com/repos/gorilla/mux/tags"""

    commit_sha: Optional[str]


@define()
class ReleaseRow:
    """https://api.github.com/repos/gorilla/mux/releases/2893151"""

    commit_sha: str = field()


@define()
class CommentRow:
    """https://api.github.com/repos/gorilla/mux/releases/2893151"""

    commit_sha: str = field()


@define()
class PullRequestRow:
    """
    https://api.github.com/repos/gorilla/mux/pulls/691
    https://api.github.com/repos/gorilla/mux/commits/e44017df2b8798f6bfff81fff1c0b319c1a54496/pulls
    """

    commit_sha: str = field()
