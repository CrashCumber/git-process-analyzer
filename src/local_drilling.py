import csv

from pydriller import Git, Repository

git = Git("/Users/valentina/Desktop/hsecourses/kp/git-process-analyzer/repos/mux")

with open("datasets/mux_no_diff.csv", "w", newline="") as f:
    writer = csv.writer(f)

    field = [
        "commit.hash",
        "commit.author.name",
        "commit.author.email",
        "commit.committer.name",
        "commit.committer.email",
        "commit.author_date",
        "commit.author_timezone",
        "commit.committer_date",
        "commit.committer_timezone",
        "commit.msg",
        "commit.branches",
        "commit.in_main_branch",
        "commit.merge",
        "commit.lines",
        "commit.insertions",
        "commit.deletions",
        "commit.files",
        "commit.parents",
        "commit.project_name",
        "commit.project_path",
        "commit.dmm_unit_size",
        "commit.dmm_unit_complexity",
        "commit.dmm_unit_interfacing",
        "commit.modified_files.added_lines",
        "commit.modified_files.deleted_lines",
        "commit.modified_files.change_type.value",
        "commit.modified_files.changed_methods",
        "commit.modified_files.methods_before",
        "commit.modified_files.complexity",
        "commit.modified_files.diff",
        "commit.modified_files.diff_parsed",
        "commit.modified_files.token_count",
        "commit.modified_files.nloc",
        "commit.modified_files.source_code",
        "commit.modified_files.source_code_before",
        "commit.modified_files.filename",
        "commit.modified_files.old_path",
        "commit.modified_files.new_path",
    ]

    writer.writerow(field)
    for commit in Repository(
        "/Users/valentina/Desktop/hsecourses/kp/git-process-analyzer/repos/mux"
    ).traverse_commits():
        modified_files = {}
        for m in commit.modified_files:
            row = [
                commit.hash,
                commit.author.name,
                commit.author.email,
                commit.committer.name,
                commit.committer.email,
                commit.author_date,
                commit.author_timezone,
                commit.committer_date,
                commit.committer_timezone,
                commit.msg,
                commit.branches,
                commit.in_main_branch,
                commit.merge,
                commit.lines,
                commit.insertions,
                commit.deletions,
                commit.files,
                commit.parents,
                commit.project_name,
                commit.project_path,
                commit.dmm_unit_size,
                commit.dmm_unit_complexity,
                commit.dmm_unit_interfacing,
                m.added_lines,
                m.deleted_lines,
                m.change_type.value,
                [i.__dict__ for i in m.changed_methods],
                [i.__dict__ for i in m.methods_before],
                m.complexity,
                "",
                # m.diff,
                m.diff_parsed,
                m.token_count,
                m.nloc,
                m.source_code,
                m.source_code_before,
                m.filename,
                m.old_path,
                m.new_path,
            ]
            writer.writerow(row)
