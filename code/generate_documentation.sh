pip install -U pip
pip install .
pip install python3-tk
rm -rf documentation/source/_autosummary
cd documentation
make html