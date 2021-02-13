import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 8080  # Port to listen on

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
msg = "I am CLIENT\n"
client.send(str.encode(msg))
while True:
    server_msg = client.recv(4096)
    print("Message from client:", server_msg)
client.close()
