#!/bin/bash
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi
python3 -u market_scanner.py --mode portfolio --tws
