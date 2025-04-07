# git ls-tree -t HEAD:./ | awk '{if ($2 == "tree") print $4;}' | grep -e '^[a-zA-Z]' > all_dir.txt

git ls-files | grep -e '^[a-zA-Z]*/test_[a-z]*\.py' > all_test_file_paths.txt

cat all_test_file_paths.txt

echo pytesting all python files in every directory

num_of_dir=$(wc -l all_test_file_paths.txt | awk ' { print $1 } ')

for i in $(seq 1 ${num_of_dir});
do
    dir_in_repo=$(sed "${i}q;d" all_test_file_paths.txt)
    pytest ${dir_in_repo} -x -vv
done

echo pytesting rest of python files in main repo
pytest . 

echo "All files tested"