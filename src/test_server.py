import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8080  # Port to listen on

# TCP socket
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((HOST, PORT))
socket.listen(5)
print("Server started...")
print("Waiting for connection...")
conn, addr = socket.accept()
print(conn, addr)
while True:
    # Receive up to 4096 bytes from a peer
    data = conn.recv(4096)
    if not data:
        break
    print("Byte data:", data)
    print("Str data:", data.decode("utf-8"))
    conn.send(data)
socket.close()
print('client disconnected')