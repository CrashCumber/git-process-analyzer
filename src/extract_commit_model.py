import os

from attrs import asdict
from github import Auth, Github

from logger import logger
from models import (CaseIdType, CommentRow, CommitRow, FileRow,
                    PullRequestCommentRow, PullRequestRow, ReleaseRow, TagRow,
                    UserEventType, UserRow)
from parsers import Counter, model_fields
from writer import prepare_file


def extract_commits(repo_name: str, branch=None, commits_cnt=None, tag_cnt=None):
    commit_file, commit_writer = prepare_file(
        model_fields(CommitRow), str(CaseIdType.commits), repo_name
    )
    file_file, file_writer = prepare_file(
        model_fields(FileRow), str(CaseIdType.file_commit), repo_name
    )
    user_file, user_writer = prepare_file(
        model_fields(UserRow), str(CaseIdType.user_commit), repo_name
    )
    pr_file, pr_writer = prepare_file(
        model_fields(PullRequestRow), str(CaseIdType.pull_commit), repo_name
    )
    prc_file, prc_writer = prepare_file(
        model_fields(PullRequestCommentRow),
        str(CaseIdType.pull_comment_commit),
        repo_name,
    )
    c_file, c_writer = prepare_file(
        model_fields(CommentRow), str(CaseIdType.comment_commit), repo_name
    )
    t_file, t_writer = prepare_file(
        model_fields(TagRow), str(CaseIdType.tag_commit), repo_name
    )
    r_file, r_writer = prepare_file(
        model_fields(ReleaseRow), str(CaseIdType.release_commit), repo_name
    )

    g = Github(auth=Auth.Token(os.getenv("git_token", "")))
    parsed_commit = set()
    parsed_pr = set()

    commit_counter = Counter()
    tag_counter = Counter()
    try:
        repo = g.get_repo(repo_name)

        if branch is None:
            branches = [repo.get_branch(repo.default_branch)]
        else:
            branches = repo.get_branches()

        tags = repo.get_tags()
        for tag in tags:
            if tag_cnt is not None and tag_counter.count >= tag_cnt:
                break
            tag_counter()
            t_writer.writerow(asdict(TagRow.from_dict(tag)))
            r = repo.get_release(tag.name)
            r_writer.writerow(asdict(ReleaseRow.from_dict(tag.commit.sha, r)))

        for branch in branches:
            for commit in repo.get_commits(sha=branch.name):
                if commit.sha in parsed_commit:
                    continue
                if commits_cnt is not None and commit_counter.count >= commits_cnt:
                    break
                parsed_commit.add(commit.sha)
                commit_counter()

                commit_writer.writerow(asdict(CommitRow.from_dict(commit)))
                user_writer.writerow(
                    asdict(
                        UserRow.from_dict(
                            commit.sha,
                            str(UserEventType.create_commit),
                            commit.author,
                            commit.commit.author,
                        )
                    )
                )
                user_writer.writerow(
                    asdict(
                        UserRow.from_dict(
                            commit.sha,
                            str(UserEventType.commit_commit),
                            commit.committer,
                            commit.commit.committer,
                        )
                    )
                )
                for f in commit.files:
                    file_writer.writerow(asdict(FileRow.from_dict(commit.sha, f)))

                for p in commit.get_pulls():
                    if p.id in parsed_pr:
                        continue
                    parsed_pr.add(p.id)
                    pr_writer.writerow(asdict(PullRequestRow.from_dict(commit.sha, p)))

                    for p in p.get_comments():
                        prc_writer.writerow(
                            asdict(PullRequestCommentRow.from_dict(commit.sha, p))
                        )

                for p in commit.get_comments():
                    c_writer.writerow(asdict(CommentRow.from_dict(commit.sha, p)))

        logger.info("Success extracted")
    except Exception as e:
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
