"" > testing_result.txt

git ls-tree -t HEAD:./ | awk '{if ($2 == "tree") print $4;}' | grep -e '^[a-zA-Z]' > all_dir.txt

echo pytesting all python files in every directory

num_of_dir=$(wc -l all_dir.txt | awk ' { print $1 } ')

for i in $(seq 1 ${num_of_dir});
do
    dir_in_repo=$(sed "${i}q;d" all_dir.txt)
    echo "Inside this directory: $dir_in_repo"
    cd "${dir_in_repo}/"
    git ls-files | grep -e '^test_[a-z_]*\.py' > all_test_files_in_dir.txt

    num_of_test_files=$(wc -l all_test_files_in_dir.txt | awk ' { print $1 } ')

    for i in $(seq 1 ${num_of_test_files});
    do
        test_file_in_repo=$(sed "${i}q;d" all_test_files_in_dir.txt)
        echo "Testing file: $test_file_in_repo"
        pytest ${test_file_in_repo} -x -vv >> ../testing_result.txt
    done
    rm all_test_files_in_dir.txt
    cd ../
done

cat testing_result.txt

echo "All files tested"

failed_test_result=$(grep -w "FAILED" testing_result.txt)
errors_test_result=$(grep -w "ERRORS" testing_result.txt)

if [[ -n "$failed_test_result" || -n "$errors_test_result" ]]; then
    echo "Failing tests present!"
    exit 1
else
    echo "All tests passed!"
fi

rm all_dir.txt
rm testing_result.txt