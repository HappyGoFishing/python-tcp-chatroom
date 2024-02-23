import socket, threading, time

CONNECT_HOST = "192.168.0.7"
CONNECT_PORT = 6675

def receive_messages_and_print(sock: socket.socket) -> None:
	while True:
		try:
			sender = sock.recv(1024).decode("utf-8")
			content = sock.recv(1024).decode("utf-8")
			print(f"\n(incoming) {sender}: {content}\n")
		except:
			break

def main() -> None:
	try:
		print(f"Starting client")
		client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_sock.connect((CONNECT_HOST, CONNECT_PORT))
		print(f"Connected to {CONNECT_HOST}:{CONNECT_PORT}")
	except Exception as e:
		print(f"Failed to connect to {CONNECT_HOST}:{CONNECT_PORT} ({e})")
		return
				
	try:
		server_name = client_sock.recv(1024).decode("utf-8")
		server_motd = client_sock.recv(1024).decode("utf-8")
		print(f"Server name: {server_name}")
		print(f"Server MOTD: {server_motd}")
		username = input("Enter username: ")
		client_sock.send(username.encode("utf-8"))

	except Exception as e:
		print(f"Failed to handshake ({e})")
		return
	receive_thread = threading.Thread(target=receive_messages_and_print, args=(client_sock,))
	receive_thread.start()
	while True:
		msg = input("Enter message (exit to quit): ")
		if msg == "quit":
			break
		client_sock.send(msg.strip().encode("utf-8"))
	client_sock.close()

	
if __name__ == "__main__":
	main()