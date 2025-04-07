git ls-tree -t HEAD:./ | awk '{if ($2 == "tree") print $4;}' | grep -e '^[a-zA-Z]' > all_dir.txt

echo pylinting all python files in every dir

num_of_dir=$(wc -l all_dir.txt | awk ' { print $1 } ')

for i in $(seq 1 ${num_of_dir});
do
    dir_in_repo=$(sed "${i}q;d" all_dir.txt)
    pylint --recursive=y ${dir_in_repo} --fail-under 8
done

echo pylinting rest of python files in main repo
pylint '*.py' --fail-under 8

echo "All files pylinted"