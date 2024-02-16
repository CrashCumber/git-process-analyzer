import os

from attrs import asdict
from github import Auth, Github

from logger import logger
from models import CaseIdType, CommitRow, FileRow, UserEventType, UserRow
from parsers import Counter, model_fields
from writer import prepare_file


def extract_commits(repo_name: str, commits_number=None, branch=None):
    commit_file, commit_writer = prepare_file(model_fields(CommitRow), str(CaseIdType.commits), repo_name)
    file_file, file_writer = prepare_file(model_fields(FileRow), str(CaseIdType.file_commit), repo_name)
    user_file, user_writer = prepare_file(model_fields(UserRow), str(CaseIdType.user_commit), repo_name)

    g = Github(auth=Auth.Token(os.getenv("git_token", "")))
    parsed_commit = set()
    counter = Counter()
    try:
        repo = g.get_repo(repo_name)
        if branch is None:
            branches = [repo.get_branch(repo.default_branch)]
        else:
            branches = repo.get_branches()

        for branch in branches:
            for commit in repo.get_commits(sha=branch.name):
                if commit.sha in parsed_commit:
                    continue
                if commits_number is not None and counter.count >= commits_number:
                    break
                parsed_commit.add(commit.sha)
                counter()

                commit_writer.writerow(asdict(CommitRow.from_dict(commit)))
                user_writer.writerow(
                    asdict(
                        UserRow.from_dict(
                            commit.sha, str(UserEventType.create_commit), commit.author, commit.commit.author
                        )
                    )
                )
                user_writer.writerow(
                    asdict(
                        UserRow.from_dict(
                            commit.sha, str(UserEventType.commit_commit), commit.committer, commit.commit.committer
                        )
                    )
                )
                for f in commit.files:
                    file_writer.writerow(asdict(FileRow.from_dict(commit.sha, f)))

        logger.info("Success extracted")
    except Exception as e:
        logger.exception("Fail to extract: %s", e)

    g.close()

    commit_file.close()
    file_file.close()
    user_file.close()
