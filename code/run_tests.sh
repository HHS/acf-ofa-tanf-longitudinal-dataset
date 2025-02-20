# Install packages
pip install -U pip
pip install .
sudo apt-get install python3-tk
sudo apt-get install -y xvfb

# Export environment variables
export DISPLAY=:0.0

# Run tests
python3 -m pytest tests/unit