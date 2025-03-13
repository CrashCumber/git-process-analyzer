files=$(ls /Users/valentina/Desktop/datasets/*/*/* | grep /Users/valentina/Desktop/datasets/ | cut -d : -f 1)
for file in $files; do
    wd="$file/"
    wr=$( echo $wd | cut -d / -f 7)
    research_path=/Users/valentina/Desktop/kp/git-process-analyzer/research/repositories/$wr.ipynb
    echo $wd $research_path
    rm $research_path
    touch $research_path
    pathTodata=$wd jupyter nbconvert --to notebook --execute research/research.ipynb --output $research_path
    if [ $? -eq 0 ]; then
        mercury add $research_path
    else
        echo $research_path >> render.log
    fi
done