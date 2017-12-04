import socket
port_number = 8080

ip_address = socket.gethostbyname(socket.gethostname())

def create_server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', port_number)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.listen(1)

    while True:
        connection, client_address = sock.accept()

if __name__ == '__main__':
    create_server_socket()
