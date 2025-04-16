"" > pylint_testing_result.txt
git ls-tree -t HEAD:./ | awk '{if ($2 == "tree") print $4;}' | grep -e '^[a-zA-Z]' > all_dir.txt

echo pylinting all python files in every dir

num_of_dir=$(wc -l all_dir.txt | awk ' { print $1 } ')

for i in $(seq 1 ${num_of_dir});
do
    dir_in_repo=$(sed "${i}q;d" all_dir.txt)
    pylint --fail-under 8.0 --recursive=y ${dir_in_repo} >> pylint_testing_result.txt
done

cat pylint_testing_result.txt

echo "All files pylinted"

test_result=$(grep -e '[a-zA-Z\s]*[0-7]\.[0-9][0-9]\/10' pylint_testing_result.txt)
if [[ -n "$test_result" ]]; then
    echo "Pylint scores below 8!"
    exit 1
else
    echo "All scores are 8 and above!"
fi

rm pylint_testing_result.txt
rm all_dir.txt