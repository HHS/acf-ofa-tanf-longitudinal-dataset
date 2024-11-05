pip install sphinx
pip install -e .
rm -rf documentation/source/_autosummary
cd documentation
make html