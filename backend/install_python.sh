#!/bin/bash

echo "Installing Python and dependencies for Linguana Backend..."
echo "============================================================"

sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib libpq-dev
sudo apt install -y redis-server
sudo apt install -y build-essential

echo ""
echo "Python installation complete!"
echo "Verifying installation..."
python3 --version
pip3 --version

echo ""
echo "Creating symbolic link for 'python' command..."
sudo apt install -y python-is-python3

echo ""
echo "Installation complete! You can now run the setup commands."
