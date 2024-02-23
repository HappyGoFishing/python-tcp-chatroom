import toml, threading, socket, time, random, sys

CONFIG_FILE_NAME = "server_config.toml"
use_fallback_config = False

FALLBACK_HOST = "localhost"
FALLBACK_PORT = 6675
FALLBACK_MOTD = "fallback motd"
FALLBACK_NAME = "fallback name"

HOST: str 
PORT: int 
MOTD: str # Message of the day
NAME: str # Name of the server

client_usernames = []
client_sockets = []

def is_item_in_list(item, list_of_items) -> bool:
	for i in list_of_items:
		if i == item:
			return True
	return False


def read_and_apply_config() -> None:
	global use_fallback_config, HOST, NAME, MOTD, PORT
	try:
		with open(CONFIG_FILE_NAME, "r") as cf:
			config_data = toml.load(cf)
			cf.close()
	except:
		print(f"{CONFIG_FILE_NAME} not found")
		use_fallback_config = True

	if use_fallback_config == False:
		try:
			HOST = config_data["network"]["host"]
			PORT = int(config_data["network"]["port"])
			MOTD = config_data["info"]["motd"]
			NAME = config_data["info"]["name"]
			print(f"Read and applied config from {CONFIG_FILE_NAME}")
		except Exception as e:
			print(f"Failed to read {CONFIG_FILE_NAME}")
			use_fallback_config = True
		
	if use_fallback_config:
		print("Using fallback config")
		HOST = FALLBACK_HOST
		PORT = FALLBACK_PORT
		MOTD = FALLBACK_MOTD
		NAME = FALLBACK_NAME


def send_broadcast(msg: str, client_list) -> None:
	for client in client_list:
		client.send(msg.encode("utf-8"))


def handle_client(client: socket.socket, addr) -> None:
	print(f"{addr} connection established")
	try:
		username: str
		#sends this server's name and motd to the client
		client.send(NAME.encode("utf-8"))
		client.send(MOTD.encode("utf-8"))
		#receive the client's username
		username = client.recv(1024).decode("utf-8")

		if not is_item_in_list(username, client_usernames):
			client_usernames.append(username)
		if not is_item_in_list(client, client_sockets):
			client_sockets.append(client)
		
		print(f"Online users: {client_usernames}")
		print(f"{addr} {username} logged on")
		
		while True:
			try:
				msg = client.recv(1024).decode("utf-8")
				if not msg:
					break
				send_broadcast(username, client_sockets)
				send_broadcast(msg, client_sockets)
				print(f"{addr} {username} sent: \"{msg}\"")
			except ConnectionResetError:
				print(f"{addr} {username} left")
				break
	except ConnectionAbortedError:
		print(f"{addr} connection aborted")
		
	finally:
		client.close()
		print(f"Closed socket {addr}")
		if is_item_in_list(username, client_usernames):
			client_usernames.remove(username)
		if is_item_in_list(client, client_sockets):
			client_sockets.remove(client)


def main() -> None:
	read_and_apply_config()
	print(f"Starting server...")
	print(f"name: {NAME}")
	print(f"MOTD: {MOTD}")
	try:
		server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_sock.bind((HOST, PORT))
		server_sock.listen(socket.SOMAXCONN)
		print(f"Listening on {HOST}:{PORT}")
		while True:
			try:
				client_sock, client_addr = server_sock.accept()
				client_thread = threading.Thread(target=handle_client, args=(client_sock, client_addr))
				client_thread.start()
			except KeyboardInterrupt:
				print("Stopping server")
				break
	except Exception as e:
		print(f"failed to start server {e}")
		return
		
	finally:
		server_sock.close()
	
if __name__ == "__main__":
	main()
