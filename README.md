# Commit Model Dataset Extractor

This script facilitates the extraction of datasets for commit models from GitHub repositories. By specifying the repository name, author, and optional parameters such as the number of commits or tags, users can customize the extraction process to suit their needs.

#### Usage

```bash
python main.py [-h] --repo REPO --author AUTHOR [--commits COMMITS]
                          [--tags TAGS] [--branch BRANCH] [--all-branch]
                          [--dir-dataset DIR_DATASET]
```

#### Arguments

- `--repo`, `-r`: Name of the GitHub repository to extract data from.
- `--author`, `-a`: Name of the repository's author or organization.
- `--commits`, `-c`: Number of commits to extract (optional). Default all.
- `--tags`, `-t`: Number of tags to extract (optional). Default all.
- `--branch`, `-b`: Specific branch to extract data from (optional). Default default branch main/master.
- `--all-branch`, `-ab`: Flag to extract all branches (optional). Default default branch main/master.
- `--dir-dataset`, `-dp`: Folder path to save the extracted dataset (optional). Default ./datasets.

#### Example

```bash
python main.py --repo git-process-analyzer --author CrashCumber --commits 100 --tags 5 --branch main --dir-dataset ./datasets
```

This command will extract 100 commits and 5 tags from the "git-process-analyzer" repository owned by "CrashCumber", specifically from the "main" branch, and save the dataset in the "./datasets" folder.

#### Dependencies

- `python 3.11`
- `make`

#### Install

```bash
git clone https://github.com/CrashCumber/git-process-analyzer.git
cd git-process-analyzer
make install

vi .env
>>
...
export git_token=your_token
...
>>

python main.py --repo git-process-analyzer --author CrashCumber --commits 100 --tags 5 --branch main --dir-dataset ./datasets
```
For more info about token [go here.](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

#### License

#### Author
