source .env
start=$(($start_from+2))

tail -n +$start $repos_file | head -n +$number_to_extract | while IFS=, read -r  rank item repo_name stars type forks language repo_url username issues last_commit description;
do
    start_extract=$(date +%s)
    venv/bin/python3 src/main.py -r $repo_name -a $username &> /dev/null;
    status=$?
    echo "$start_extract,$(date +%s),$rank,$repo_name,$status" >> status.csv;
done