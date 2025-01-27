# Activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install packages
pip install -U pip
pip install .
pip install beautifulsoup4 lxml
pip install python3-tk

# Remove old documentation and regenerate
rm -rf documentation/source/_autosummary
cd documentation
make html

cd ..