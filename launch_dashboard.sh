#!/bin/bash

# Intervalul de actualizare în secunde (3600 = 1 oră)
INTERVAL=3600
PYTHON_BIN=".venv/bin/python"
if [ ! -x "$PYTHON_BIN" ]; then
    PYTHON_BIN="/usr/local/bin/python3.13"
fi

echo "=== Market Scanner Automation Started ==="
echo "Scanner-ul va rula la fiecare $INTERVAL secunde."
echo "Pentru a opri, apasă CTRL+C sau închide terminalul (dacă rulează în foreground)."

while true; do
    echo "[$(date)] Rulare scanner..."
    "$PYTHON_BIN" market_scanner.py
    
    echo "[$(date)] Finalizat. Următoarea rulare peste 1 oră."
    sleep $INTERVAL
done
