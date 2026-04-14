#!/bin/bash

# TimeKpr Network Manager - Universeel Installatie Script
# Ondersteunt: Ubuntu/Debian, Fedora, openSUSE, Arch Linux

set -e # Stop bij fouten

echo "--- TimeKpr Network Manager Installatie ---"

# 1. Detecteer de Linux distributie
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Fout: Kan besturingssysteem niet detecteren."
    exit 1
fi

echo "Gedetecteerd systeem: $PRETTY_NAME"

# 2. Installeer systeem-afhankelijkheden op basis van de package manager
case "$OS" in
    ubuntu|debian|linuxmint|pop)
        echo "Installeren via apt..."
        sudo apt update
        sudo apt install -y nmap python3-pyqt6 python3-paramiko python3-psutil python3-pip
        # python-nmap is vaak niet als deb pakket beschikbaar, dus via pip
        sudo pip3 install python-nmap --break-system-packages || pip3 install python-nmap
        ;;
    fedora)
        echo "Installeren via dnf..."
        sudo dnf install -y nmap python3-pyqt6 python3-paramiko python3-psutil python3-pip
        sudo pip3 install python-nmap
        ;;
    opensuse*|suse)
        echo "Installeren via zypper..."
        sudo zypper install -y nmap python313-qt6 python313-paramiko python313-psutil python313-python-nmap
        ;;
    arch|manjaro)
        echo "Installeren via pacman..."
        sudo pacman -Sy --noconfirm nmap python-pyqt6 python-paramiko python-psutil python-nmap
        ;;
    *)
        echo "Onbekende distributie: $OS. We proberen een algemene pip installatie..."
        sudo pip3 install PyQt6 paramiko psutil python-nmap --break-system-packages || echo "Pip installatie mislukt, installeer afhankelijkheden handmatig."
        ;;
esac

# 3. Paden configureren
APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIN_PATH="/usr/bin/python3"
if [ ! -f "$BIN_PATH" ]; then
    BIN_PATH=$(which python3)
fi

echo "Applicatie map: $APP_DIR"
echo "Python pad: $BIN_PATH"

# 4. Opstartscript maken
CAT_SCRIPT="$APP_DIR/timekpr-network-manager.sh"
echo "Aanmaken opstartscript..."
cat <<EOF > "$CAT_SCRIPT"
#!/bin/bash
cd "$APP_DIR"
"$BIN_PATH" gui.py
EOF
chmod +x "$CAT_SCRIPT"

# 5. Desktop Entry maken voor het menu
DESKTOP_FILE="$HOME/.local/share/applications/timekpr-network-manager.desktop"
mkdir -p "$HOME/.local/share/applications"

echo "Toevoegen aan startmenu..."
cat <<EOF > "$DESKTOP_FILE"
[Desktop Entry]
Name=TimeKpr Network Manager
Comment=Beheer TimeKpr op je netwerk via SSH
Exec="$CAT_SCRIPT"
Path="$APP_DIR"
Icon=timekpr
Terminal=false
Type=Application
Categories=Settings;System;
Keywords=timekpr;limits;parental;
StartupNotify=true
EOF

# 6. Cache verversen (vooral voor KDE/openSUSE)
if command -v kbuildsycoca6 &> /dev/null; then kbuildsycoca6 &> /dev/null; fi
if command -v kbuildsycoca5 &> /dev/null; then kbuildsycoca5 &> /dev/null; fi
if command -v update-desktop-database &> /dev/null; then update-desktop-database ~/.local/share/applications &> /dev/null; fi

echo "--------------------------------------------------------"
echo "INSTALLATIE VOLTOOID!"
echo "Je kunt 'TimeKpr Network Manager' nu vinden in je menu."
echo "--------------------------------------------------------"
