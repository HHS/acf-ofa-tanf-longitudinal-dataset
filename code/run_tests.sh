# Install packages
pip install -U pip
pip install .
sudo apt-get install python3-tk

# Run tests
python3 -m pytest tests/unit

# If tests fail, exit with status 1, probably not needed
# result=$(echo $?)
# if [ $result != 0 ]; then
#     exit 1
# fi