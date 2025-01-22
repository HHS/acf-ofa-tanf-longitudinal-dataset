# Install packages
pip install -U pip
pip install .
pip install beautifulsoup4 
pip install python3-tk

# Remove old documentation and regenerate
rm -rf documentation/source/_autosummary
cd documentation
make html

cd ..