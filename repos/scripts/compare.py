import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

TARGET = "2023-01-18"
datas = sorted(
    [
        *[f"2022-{i:02d}-01" for i in range(1, 12)],
        TARGET,
        *[f"2023-{i:02d}-01" for i in range(1, 13)],
        *[f"2024-{i:02d}-01" for i in range(1, 3)],
    ]
)

report_path = "report.md"
report_f = open(report_path, mode="w")
report_f.write(f"### Reference date: {TARGET}\n\n")

for data in datas:
    data_path = f"datas/{data}"
    if os.path.exists(data_path):
        continue
    ds = requests.get(f"https://raw.githubusercontent.com/EvanLi/Github-Ranking/master/Data/github-ranking-{data}.csv")
    with open(data_path, mode="w") as f:
        f.write(ds.content.decode())

df_raw = pd.read_csv(f"datas/{TARGET}")
df_target = df_raw.loc[df_raw["item"] == "Go"]

res = []
res_added_repos = []
res_removed_repos = []
for data in datas:
    data_path = f"datas/{data}"
    df_compare_raw = pd.read_csv(data_path)
    df_compare = df_compare_raw.loc[df_compare_raw["item"] == "Go"]

    matching_repos = len(set(df_target["repo_name"]).intersection(set(df_compare["repo_name"])))
    res.append(matching_repos)

    added_repos = set(df_compare["repo_name"]).difference(set(df_target["repo_name"]))
    res_added_repos.append(len(added_repos))
    removed_repos = set(df_target["repo_name"]).difference(set(df_compare["repo_name"]))
    res_removed_repos.append(len(removed_repos))

data = {"Date": datas, "Matching number": res, "Added number": res_added_repos, "Removed number": res_removed_repos}
df = pd.DataFrame(data)

report_f.write(df.to_markdown())
table = open("report.xls", mode="wb")
df.to_excel(table)
table.close()

df["Date"] = pd.to_datetime(df["Date"])

plt.figure(figsize=(10, 6))
plt.plot(df["Date"], df["Matching number"], marker="o")
plt.title("The dependence of the date on the number of immutable repositories")
plt.xlabel("Date")
plt.ylabel("Matching number")
plt.grid(True)

plt.xticks(rotation=45)
plt.tight_layout()

plt.ylim(0, 100)

highlight_date = pd.to_datetime("2023-01-18")
highlight_value = df.loc[df["Date"] == highlight_date, "Matching number"].values[0]
plt.scatter(highlight_date, highlight_value, color="red", zorder=5)
plt.axvline(x=highlight_date, color="red", linestyle="--", linewidth=1)
average = np.mean(res)

report_f.write(f"\n\nAvarage: {average}\n")

plt.axhline(y=average, color="green", linestyle="--", linewidth=1)
plt.savefig("plt.png")

report_f.write("\n\n![](plt.png)\n")
report_f.close()
