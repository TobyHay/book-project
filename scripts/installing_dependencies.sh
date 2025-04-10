git ls-tree -t HEAD:./ | awk '{if ($2 == "tree") print $4;}' | grep -e '^[a-zA-Z]' > all_dir.txt

num_of_dir=$(wc -l all_dir.txt | awk ' { print $1 } ')

if [[ "$num_of_dir" != "0" ]]; then
    for i in $(seq 1 ${num_of_dir});
    do
        dir_in_repo=$(sed "${i}q;d" all_dir.txt)
        
        if [[ "$dir_in_repo" == "terraform" ]]; then
            echo "Ignoring Terraform folder"
            continue
        fi

        if test -f ${dir_in_repo}/requirements.txt; then
            cd ${dir_in_repo}
            echo ${dir_in_repo}
            pip install -r requirements.txt
            cd ../
        fi
    done
else
    echo "No directories to work with"
fi

echo "Dependencies installed"