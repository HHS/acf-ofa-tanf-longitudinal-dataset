pip install -U pip
pip install .
rm -rf documentation/source/_autosummary
cd documentation
make html