import os
import time

from github import Auth, Github
from github.GithubException import UnknownObjectException

from logger import logger
from models import (
    CaseIdType,
    CommentRow,
    CommitRow,
    FileRow,
    PullRequestCommentRow,
    PullRequestRow,
    ReleaseRow,
    TagRow,
    UserEventType,
    UserRow,
)
from utils import Counter, model_fields
from writer import prepare_file


def extract_commits(repo_name: str, all_branch=True, branch=None, commits_cnt=None, tag_cnt=None, dir_dataset=None):
    timestamp = str(int(time.time()))
    commit_file, commit_writer = prepare_file(
        model_fields(CommitRow),
        str(CaseIdType.commits),
        repo_name,
        timestamp,
        dir_dataset,
    )
    file_file, file_writer = prepare_file(
        model_fields(FileRow),
        str(CaseIdType.file_commit),
        repo_name,
        timestamp,
        dir_dataset,
    )
    user_file, user_writer = prepare_file(
        model_fields(UserRow),
        str(CaseIdType.user_commit),
        repo_name,
        timestamp,
        dir_dataset,
    )
    pr_file, pr_writer = prepare_file(
        model_fields(PullRequestRow),
        str(CaseIdType.pull_commit),
        repo_name,
        timestamp,
        dir_dataset,
    )
    prc_file, prcomment_writer = prepare_file(
        model_fields(PullRequestCommentRow),
        str(CaseIdType.pull_comment_commit),
        repo_name,
        timestamp,
        dir_dataset,
    )
    c_file, comment_writer = prepare_file(
        model_fields(CommentRow),
        str(CaseIdType.comment_commit),
        repo_name,
        timestamp,
        dir_dataset,
    )
    t_file, tag_writer = prepare_file(
        model_fields(TagRow),
        str(CaseIdType.tag_commit),
        repo_name,
        timestamp,
        dir_dataset,
    )
    r_file, release_writer = prepare_file(
        model_fields(ReleaseRow),
        str(CaseIdType.release_commit),
        repo_name,
        timestamp,
        dir_dataset,
    )

    g = Github(auth=Auth.Token(os.getenv("git_token", "")))

    commit_counter = Counter()
    tag_counter = Counter()
    try:
        repo = g.get_repo(repo_name)

        if branch:
            branches = [repo.get_branch(branch)]
        elif all_branch:
            branches = repo.get_branches()
        else:
            branches = [repo.get_branch(repo.default_branch)]

        tags = repo.get_tags()
        for tag in tags:
            if tag_cnt is not None and tag_counter.count >= tag_cnt:
                break
            tag_counter()
            sha = tag.commit.sha
            tag_writer.writerow(TagRow.from_dict(tag))
            try:
                release = repo.get_release(tag.name)
            except UnknownObjectException:
                logger.info("no release for tag %s", tag.name)
            else:
                release_writer.writerow(ReleaseRow.from_dict(sha, release))
                user_writer.writerow(
                    UserRow.from_dict(
                        sha,
                        UserEventType.create_release,
                        release.author,
                        release.created_at,
                    )
                )

        for branch in branches:
            for commit in repo.get_commits(sha=branch.name):
                sha = commit.sha
                if commits_cnt is not None and commit_counter.count >= commits_cnt:
                    break

                logger.info("commit %s:%s", branch.name, sha)
                commit_counter()
                commit_writer.writerow(CommitRow.from_dict(commit, branch.name))
                if commit.author:
                    user_writer.writerow(
                        UserRow.from_dict(
                            sha,
                            UserEventType.create_commit,
                            commit.author,
                            commit.commit.author.date,
                        )
                    )

                if commit.committer:
                    user_writer.writerow(
                        UserRow.from_dict(
                            sha,
                            UserEventType.commit_commit,
                            commit.committer,
                            commit.commit.committer.date,
                        )
                    )
                for f in commit.files:
                    file_writer.writerow(FileRow.from_dict(sha, f))

                for pull in commit.get_pulls():
                    pr_writer.writerow(PullRequestRow.from_dict(sha, pull))

                    if pull.user:
                        user_writer.writerow(
                            UserRow.from_dict(
                                sha,
                                UserEventType.create_pull_request,
                                pull.user,
                                pull.created_at,
                            )
                        )
                    if pull.merged_by:
                        user_writer.writerow(
                            UserRow.from_dict(
                                sha,
                                UserEventType.merge_pull_request,
                                pull.merged_by,
                                pull.merged_at,
                            )
                        )
                    try:
                        pull_comments = pull.get_comments()
                    except Exception as exp:
                        logger.exception(exp)
                        pull_comments = []

                    for pull_comment in pull_comments:
                        if pull_comment.commit_id != sha:
                            continue
                        prcomment_writer.writerow(PullRequestCommentRow.from_dict(sha, pull_comment))

                        if pull_comment.user:
                            user_writer.writerow(
                                UserRow.from_dict(
                                    sha,
                                    UserEventType.comment_pull_request,
                                    pull_comment.user,
                                    pull_comment.created_at,
                                )
                            )
                    del pull_comments

                    for reviewer in pull.requested_reviewers:
                        user_writer.writerow(
                            UserRow.from_dict(
                                sha,
                                UserEventType.requested_review_from,
                                reviewer,
                                None,
                            )
                        )
                    for assign in pull.assignees:
                        user_writer.writerow(
                            UserRow.from_dict(
                                sha,
                                UserEventType.assigned_to,
                                assign,
                                None,
                            )
                        )
                try:
                    comments = commit.get_comments()
                except Exception as exp:
                    logger.exception(exp)
                    comments = []

                for comment in comments:
                    comment_writer.writerow(CommentRow.from_dict(sha, comment))
                    user_writer.writerow(
                        UserRow.from_dict(
                            sha,
                            UserEventType.comment_commit,
                            comment.user,
                            comment.created_at,
                        )
                    )
                del commit
                del comments

        logger.info("Success extracted")
        status = 0
    except Exception as e:
        status = 1
        logger.exception("Fail to extract: %s", e)

    g.close()

    commit_file.close()
    file_file.close()
    user_file.close()
    pr_file.close()
    prc_file.close()
    c_file.close()
    t_file.close()
    r_file.close()
    return status
