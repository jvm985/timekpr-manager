#!/bin/bash
echo "Bezig met installeren van systeem afhankelijkheden..."
sudo apt update
sudo apt install -y nmap python3-pip python3-pyqt6

echo "Bezig met installeren van Python bibliotheken..."
pip3 install -r requirements.txt --break-system-packages

echo "Gereed! Je kunt de app nu starten met: python3 gui.py"
