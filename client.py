import socket

def start_client(server_ip, server_port):
    # 1. The client creates a socket and connects to ‘localhost’ and port xxxx
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))

    # 4. The client calls recv to receive data
    introduction = client.recv(4096).decode()
    # 5. The client prints the data
    print(introduction)

    while True:
        # 2. When connected, the client prompts for a message to send
        command = input("Enter command: ")

        # The player can type 'quit' or 'exit' to break out of the loop
        if command.lower() in ["quit", "exit"]:
            # 7. Sockets are closed (can use with in python3)
            break

        # 3. The client sends the message
        client.send(command.encode())
        
        # 4. The client calls recv to receive data
        response = client.recv(4096).decode()
        # 5. The client prints the data
        print(response)

    # 7. Sockets are closed (can use with in python3)
    client.close()

if __name__ == "__main__":
    SERVER_IP = 'localhost'
    SERVER_PORT = 12345  # Must match the server's port
    start_client(SERVER_IP, SERVER_PORT)
