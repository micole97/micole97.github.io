#!/bin/bash
cd "$(dirname "$0")/admin"
if [ ! -d venv ]; then
  python3 -m venv venv
  ./venv/bin/pip install --quiet --upgrade pip
  ./venv/bin/pip install --quiet -r requirements.txt
fi
./venv/bin/python app.py &
SERVER_PID=$!
sleep 1
open http://127.0.0.1:5151/
echo "Admin portal running. Close this window (or press Ctrl+C) to stop it."
wait $SERVER_PID
