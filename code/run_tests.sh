# Install packages
pip install -U pip
pip install .

# Run tests
python3 -m unittest discover tests/

# If tests fail, exit with status 1, probably not needed
# result=$(echo $?)
# if [ $result != 0 ]; then
#     exit 1
# fi