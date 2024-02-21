import socket, time

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("localhost", 6675))
print(sock.recv(1024).decode("utf-8"))
print(sock.recv(1024).decode("utf-8"))
sock.send("kieran".encode("utf-8"))