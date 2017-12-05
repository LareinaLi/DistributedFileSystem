import socket
import threadpool
import file_server_model

port_number = 8080
ip_address = socket.gethostbyname(socket.gethostname())

server_thread_pool = threadpool.ThreadPool(500)
file_system_manager = file_server_model.FileSystemManager('FileSystemDirectory')

def create_server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', port_number)
    print('starting up on %s port %s' % server_address)
    sock.bind(server_address)
    sock.listen(1)

    while True:
        connection, client_address = sock.accept()
        server_thread_pool.add_task(start_client_interaction, connection)

def start_client_interaction(connection):
    try:
        client_id = file_system_manager.add_client(connection)
        while True:
            data = connection.recv(1024).decode()
            split_data = data.split('////')
            
            if data == 'KILL_SERVICE':
                response = 'Killing Service'
                connection.sendall(response.encode())
                connection.close()
                os._exit(0)
                
            elif split_data[0] == 'exit':
                if len(split_data) == 1:
                    file_system_manager.disconnect_client(connection, client_id)
                else:
                    error_response(connection, 1)
            else:
                error_response(connection, 1)
    except:
        error_response(connection, 0)
        connection.close()
        
def error_response(connection, error_code):
    if error_code == 0:
        response = 'Server error\n'
    if error_code == 1:
        response = 'Unrecognised command\n'
    connection.sendall(response.encode())
        
if __name__ == '__main__':
    create_server_socket()
