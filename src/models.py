import enum

from attrs import define, field
from github.Commit import Commit
from github.CommitComment import CommitComment
from github.File import File
from github.GitAuthor import GitAuthor
from github.GitRelease import GitRelease
from github.NamedUser import NamedUser
from github.PullRequest import PullRequest
from github.PullRequestComment import PullRequestComment
from github.Tag import Tag


class CaseIdType(enum.StrEnum):
    user_commit = "user_commit"
    pull_commit = "pull_request_commit"
    pull_comment_commit = "pull_request_comment_commit"
    file_commit = "file_commit"
    comment_commit = "comment_commit"
    commits = "commits"
    tag_commit = "tag_commit"
    release_commit = "release_commit"


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
class CommitRow:
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


@define()
class FileRow:
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


@define()
class UserRow:
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
    following_url: str = field()
    subscriptions_url: str = field()
    organizations_url: str = field()
    repos_url: str = field()
    received_events_url: str = field()
    site_admin: bool = field(converter=bool)
    type: str = field()
    company: str = field()
    following: int = field(default=None)
    followers: int = field(default=None)

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


@define()
class CommentRow:
    commit_sha: str = field()
    body: str = field()
    id: str = field()
    created_at: str = field()
    updated_at: str = field()

    @classmethod
    def from_dict(cls, commit_sha: str, cmt: CommitComment):
        row = {
            "commit_sha": cmt.commit_id,
            "id": cmt.id,
            "body": cmt.body,
            "created_at": cmt.created_at,
            "updated_at": cmt.updated_at,
        }
        return cls(**row)


@define()
class PullRequestRow:
    commit_sha: str = field()
    id: int = field()
    number: int = field()
    state: str = field()
    body: str = field()
    title: str = field()
    created_at: str = field()
    updated_at: str = field()
    closed_at: str = field()
    merged_at: str = field()
    draft: bool = field()

    @classmethod
    def from_dict(cls, commit_sha: str, pull_request: PullRequest):
        row = {
            "commit_sha": commit_sha,
            "id": pull_request.id,
            "number": pull_request.number,
            "state": pull_request.state,
            "body": pull_request.body,
            "title": pull_request.title,
            "created_at": pull_request.created_at,
            "updated_at": pull_request.updated_at,
            "closed_at": pull_request.closed_at,
            "merged_at": pull_request.merged_at,
            "draft": pull_request.draft,
        }
        return cls(**row)


@define()
class PullRequestCommentRow:
    commit_sha: str = field()
    body: str = field()
    id: str = field()
    created_at: str = field()
    updated_at: str = field()

    @classmethod
    def from_dict(cls, commit_sha: str, cmt: PullRequestComment):
        row = {
            "commit_sha": cmt.commit_id,
            "id": cmt.id,
            "body": cmt.body,
            "created_at": cmt.created_at,
            "updated_at": cmt.updated_at,
        }
        return cls(**row)


@define()
class TagRow:
    commit_sha: str = field()
    name: str = field()

    @classmethod
    def from_dict(cls, tag: Tag):
        row = {
            "commit_sha": tag.commit.sha,
            "name": tag.name,
        }
        return cls(**row)


@define()
class ReleaseRow:
    commit_sha: str = field()
    tag_name: str = field()
    body: str = field()
    author_id: str = field()
    author_name: str = field()
    created_at: str = field()
    published_at: str = field()
    id: str = field()
    title: str = field()
    target_commitish: str = field()
    draft: bool = field()
    prerelease: bool = field()

    @classmethod
    def from_dict(cls, commit_sha, release: GitRelease):
        row = {
            "commit_sha": commit_sha,
            "id": release.id,
            "tag_name": release.tag_name,
            "created_at": release.created_at,
            "published_at": release.published_at,
            "title": release.title,
            "prerelease": release.prerelease,
            "draft": release.draft,
            "target_commitish": release.target_commitish,
            "author_name": release.author.name,
            "author_id": release.author.id,
            "body": release.body,
        }
        return cls(**row)
