import socket
import threading
import os
import hashlib

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server running at {self.host}:{self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            try:
                msg = client_socket.recv(1024).decode()
                if msg:
                    print(f"Received message: {msg}")
                    self.broadcast(msg, client_socket)
            except ConnectionResetError:
                break
        client_socket.close()

    def broadcast(self, msg, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                client.send(msg.encode())

class P2PClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def connect_to_peer(self):
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((self.host, self.port))
        threading.Thread(target=self.receive_messages, args=(peer_socket,)).start()
        return peer_socket

    def receive_messages(self, peer_socket):
        while True:
            msg = peer_socket.recv(1024).decode()
            if msg:
                print(f"Message from peer: {msg}")

    def send_file(self, peer_socket, file_path):
        if os.path.exists(file_path):
            file_name = os.path.basename(file_path)
            peer_socket.send(f"Sending file: {file_name}".encode())
            with open(file_path, 'rb') as file:
                while (chunk := file.read(1024)):
                    peer_socket.send(chunk)
            print(f"File {file_name} sent successfully.")
        else:
            print("File does not exist.")

    def listen_for_files(self, peer_socket):
        while True:
            msg = peer_socket.recv(1024).decode()
            if "Sending file:" in msg:
                file_name = msg.split(":")[1].strip()
                self.receive_file(peer_socket, file_name)

    def receive_file(self, peer_socket, file_name):
        with open(file_name, 'wb') as file:
            while True:
                chunk = peer_socket.recv(1024)
                if not chunk:
                    break
                file.write(chunk)
        print(f"File {file_name} received successfully.")

    def calculate_file_hash(self, file_path):
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

def main():
    mode = input("Start as server (s) or client (c)? ")
    host = input("Enter host (or IP address): ")
    port = int(input("Enter port number: "))

    if mode.lower() == 's':
        peer = Peer(host, port)
        peer.start_server()
    elif mode.lower() == 'c':
        client = P2PClient(host, port)
        peer_socket = client.connect_to_peer()
        threading.Thread(target=client.listen_for_files, args=(peer_socket,)).start()

        while True:
            action = input("Enter 'send' to send a file or 'exit' to quit: ")
            if action.lower() == 'send':
                file_path = input("Enter the file path: ")
                client.send_file(peer_socket, file_path)
            elif action.lower() == 'exit':
                break

if __name__ == "__main__":
    main()