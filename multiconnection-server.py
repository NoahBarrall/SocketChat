import sys
import socket
import selectors
import types
import threading

sel = selectors.DefaultSelector()

def accept_wrapper(sock):
    conn, addr = sock.accept()
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Read incoming message
        if recv_data:
            print(f"Received message: {recv_data.decode('utf-8')}")
            # Do something with the received data here (no echoing unless needed)
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()

    # Only send a response if there is something to send
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print(f"Sending response to {data.addr}")
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


def start_server(host, port):
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print(f"Server listening on {(host, port)}")
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)

    try:
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
    except KeyboardInterrupt:
        print("Caught keyboard interrupt, exiting")
    finally:
        sel.close()

if __name__ == "__main__":
    host, port = sys.argv[1], int(sys.argv[2])
    server_thread = threading.Thread(target=start_server, args=(host, port), daemon=True)
    server_thread.start()

    # Accept manual input for messages to broadcast to all clients
    while True:
        message = input("Enter message to send to all clients: ").encode()
        for key in sel.get_map().values():
            if key.data:  # Only for connected clients
                key.data.outb += message
