"" > testing_result.txt

git ls-tree -t HEAD:./ | awk '{if ($2 == "tree") print $4;}' | grep -e '^[a-zA-Z]' > all_dir.txt

git ls-files | grep -e '^[a-zA-Z]*/test_[a-z]*\.py' > all_test_file_paths.txt

echo pytesting all python files in every directory

num_of_dir=$(wc -l all_test_file_paths.txt | awk ' { print $1 } ')

for i in $(seq 1 ${num_of_dir});
do
    test_file_in_repo=$(sed "${i}q;d" all_test_file_paths.txt)
    echo "Testing file from this path: $test_file_in_repo"
    pytest ${test_file_in_repo} -x -vv >> testing_result.txt
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