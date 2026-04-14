#!/bin/bash
# Log file location
LOGFILE="/home/joachim/develop/time/startup.log"
echo "--- Opstarten op $(date) ---" > "$LOGFILE"

# Verander naar de projectmap
cd /home/joachim/develop/time/ >> "$LOGFILE" 2>&1

# Zorg dat de DISPLAY variabele correct is (voor X11)
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
    echo "DISPLAY was leeg, ingesteld op :0" >> "$LOGFILE"
fi

# Zorg voor Wayland ondersteuning (indien van toepassing)
if [ -z "$XDG_RUNTIME_DIR" ]; then
    export XDG_RUNTIME_DIR=/run/user/$(id -u)
    echo "XDG_RUNTIME_DIR ingesteld op /run/user/$(id -u)" >> "$LOGFILE"
fi

# Start de app met het volledige pad naar python3
echo "Start python app..." >> "$LOGFILE"
/usr/bin/python3 /home/joachim/develop/time/gui.py >> "$LOGFILE" 2>&1

if [ $? -ne 0 ]; then
    echo "App afgesloten met foutcode: $?" >> "$LOGFILE"
fi
