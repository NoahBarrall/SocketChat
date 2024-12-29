import socket
import sys
import threading

def receive_messages(sock):
    while True:
        try:
            data = sock.recv(1024)
            if data:
                print(f"Server: {data.decode('utf-8')}")
            else:
                print("Disconnected from server")
                break
        except ConnectionError:
            print("Connection error")
            break

def start_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        print(f"Connected to server at {(host, port)}")

        thread = threading.Thread(target=receive_messages, args=(sock,), daemon=True)
        thread.start()

        while True:
            message = input("You (emojis allowed): ")
            if message.lower() == "exit":
                print("Exiting chat...")
                break
            sock.sendall(message.encode('utf-8'))

if __name__ == "__main__":
    host, port = sys.argv[1], int(sys.argv[2])
    start_client(host, port)