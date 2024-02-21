import toml, threading, socket, time

CONFIG_FILE_NAME = "server_config.toml"
use_fallback_config = False

FALLBACK_HOST = "localhost"
FALLBACK_PORT = 1000
FALLBACK_MOTD = "fallback motd"
FALLBACK_NAME = "fallback name"
HOST: str
PORT: int
MOTD: str
NAME: str

def read_and_apply_config() -> None:
	global HOST
	global PORT
	global MOTD
	global NAME
	global use_fallback_config

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
			print(f"Applied settings from {CONFIG_FILE_NAME}")
		except Exception as e:
			print(f"Failed to read {CONFIG_FILE_NAME}")
			use_fallback_config = True
		
	if use_fallback_config:
		print("Using fallback config")
		HOST = FALLBACK_HOST
		PORT = FALLBACK_PORT
		MOTD = FALLBACK_MOTD
		NAME = FALLBACK_NAME

def handle_client(client: socket.socket) -> None:
	client_username = ""
	while True:
		try:
			#sending the server name and motd
			client.send(NAME.encode("utf-8"))
			client.send(MOTD.encode("utf-8"))
			#receive client's username
			client_username = client.recv(1024).decode("utf-8")
		except ConnectionResetError:
			print("discon")
			return


def main() -> None:
	read_and_apply_config()
	print(f"Starting server {HOST}:{PORT}")
	try:
		server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_sock.bind((HOST, PORT))
		server_sock.listen(socket.SOMAXCONN)
		while True:
			try:
				client_sock, client_addr = server_sock.accept()
				client_thread = threading.Thread(target=handle_client, args=(client_sock,)).start()
			except KeyboardInterrupt:
				print("stopping server")
				break
	except Exception as e:
		print(f"failed to start server {e}")
		return
	finally:
		server_sock.close()

if __name__ == "__main__":
	main()
