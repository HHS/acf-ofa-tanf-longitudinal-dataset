pip install sphinx
python -m pip install .
rm -rf documentation/source/_autosummary
cd documentation
make html