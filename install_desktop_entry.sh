#!/bin/bash
# Zorg dat de map bestaat
mkdir -p ~/.local/share/applications

# Schrijf de desktop file die DIRECT de python app aanroept
# Dit is stabieler voor taakbalk-beheer
cat <<EOF > ~/.local/share/applications/timekpr-network-manager.desktop
[Desktop Entry]
Name=TimeKpr Network Manager
Comment=Beheer TimeKpr op je netwerk via SSH
Exec=/usr/bin/python3 /home/joachim/develop/time/gui.py
Path=/home/joachim/develop/time/
Icon=timekpr
Terminal=false
Type=Application
Categories=Settings;System;
Keywords=timekpr;limits;parental;
StartupNotify=true
X-KDE-SubstituteUID=false
EOF

# Forceer update van menu/taakbalk cache op openSUSE (KDE)
if command -v kbuildsycoca6 &> /dev/null; then
    kbuildsycoca6 &> /dev/null
elif command -v kbuildsycoca5 &> /dev/null; then
    kbuildsycoca5 &> /dev/null
fi

echo "Snelkoppeling vernieuwd. Verwijder a.u.b. het oude icoon van je taakbalk en pin de app opnieuw vanuit het startmenu."
