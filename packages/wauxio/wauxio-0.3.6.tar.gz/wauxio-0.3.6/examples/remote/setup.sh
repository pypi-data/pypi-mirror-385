#!/bin/bash

echo "[=] Installation..."

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[-] Creating virtual environment..."
    python3 -m venv .venv
    echo "[+] Virtual environment created"
fi

# Activate virtual environment
echo "[-] Activating virtual environment..."
source .venv/bin/activate
echo "[+] Virtual environment activated"

# Install dependencies
echo "[-] Updating pip..."
pip install --upgrade pip
echo "[+] Updated pip"

echo "[-] Installing requirements..."
pip install -r requirements.txt
echo "[+] Installed requirements"

# Ask user to install wauxio from PyPI, locally specified path, or default ../..
echo "[=] Select where to install from wauxio library:"
echo "To install from local source enter path (or leave empty: default ../..)"
echo "? to install from PyPI"
echo "* to skip installation"
read -p "<path>/<>/<?>/<*>: " option

if [ "$option" == "*" ]; then
    echo "[+] wauxio installation skipped"
elif [ "$option" == "?" ]; then
    echo "[-] Installing wauxio from PyPI..."
    pip install wauxio
    echo "[+] Installed wauxio"
elif [ -z "$option" ]; then
    echo "[-] Installing wauxio from ../.."
    # pip install -e ../..
    pip install ../..
    echo "[+] Installed wauxio"
else
    echo "[-] Installing wauxio from $option"
    # pip install -e "$option"
    pip install "$option"
    echo "[+] Installed wauxio"
fi

echo "[=] Installation finished"
