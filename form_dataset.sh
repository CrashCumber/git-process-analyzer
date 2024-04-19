source .env
start=$(($start_from+2))

tail -n +$start $repos_file | head -n +$number_to_extract | while IFS=, read -r  rank item repo_name stars type forks language repo_url username issues last_commit description;
do
    echo "Parse: $rank $repo_name $username" >> form_dataset.log;
    timest=$(date +%s);
    venv/bin/python3 src/main.py -r $repo_name -a $username &> /dev/null;
    echo "$timest,$repo_name,$?" >> status.log;
done