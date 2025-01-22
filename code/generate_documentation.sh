# Install packages
pip install -U pip
pip install .
pip install beautifulsoup4 python3-tk

# Remove old documentation and regenerate
rm -rf documentation/source/_autosummary
cd documentation
make html

# Add transformation documentation
cd ..
# bash code/make_html_documentation.sh
# python3 -m code/update_index.py