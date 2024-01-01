import os

from github import Auth, Github

from logger import logger
from parsers import (
    extract_comment,
    extract_commit,
    extract_file,
    extract_git_commit,
    extract_pull_request,
)
from writer import write_dataset


def extract_all_commits_dataset(repo_name: str):
    logger.info("Start extract data from %s", repo_name)
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

    logger.info("Processed branches %d", process_branches)
    logger.info(
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
    logger.info("Processed tags %d", process_tags)
    logger.info(
        "Processed tags commits %d, some times %d",
        process_tags_commits,
        process_tags_commits_twice,
    )

    g.close()
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
    write_dataset(commits, fieldnames, "unique_commits", repo_name)
