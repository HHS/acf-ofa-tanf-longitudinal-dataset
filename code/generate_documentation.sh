pip install sphinx
pip install setuptools
pip install -e .
rm -rf documentation/source/_autosummary
cd documentation
make html