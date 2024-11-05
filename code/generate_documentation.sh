pip install sphinx
pip install "setuptools>=61.0"
pip install -e .
rm -rf documentation/source/_autosummary
cd documentation
make html