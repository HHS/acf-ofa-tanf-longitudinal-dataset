pip install sphinx
pip install .
rm -rf documentation/source/_autosummary
cd documentation
make html