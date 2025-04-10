"" > testing_result.txt
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

test_result=$(grep -w "FAILED" testing_result.txt)
if [[ -n "$test_result" ]]; then
    echo "Failing tests present!"
    exit 1
else
    echo "All tests passed!"
fi