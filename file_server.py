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
            elif split_data[0] == 'ls':
                if len(split_data) == 1:
                    response = file_system_manager.list_directory_contents(client_id) + '\n'
                    connection.sendall(response.encode())
                elif len(split_data) == 2:
                    response = file_system_manager.list_directory_contents(client_id, split_data[1]) + '\n'
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)
            elif split_data[0] == 'cd':
                if len(split_data) == 2:
                    res = file_system_manager.change_directory(split_data[1], client_id)
                    response = ''
                    if res == 0:
                        response = 'Changed directory to' + split_data[1] + '\n'
                    elif res == 1:
                        response = 'Directory' + split_data[1] + 'does not exist\n'
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)
            elif split_data[0] == 'up':
                
            elif split_data[0] == 'read':
                
            elif split_data[0] == 'write':
                
            elif split_data[0] == 'delete':
                
            elif split_data[0] == 'lock':
                
            elif split_data[0] == 'release':
                
            elif split_data[0] == 'mkdir':
                
            elif split_data[0] == 'rmdir':
                
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
    server_thread_pool.wait_completion()
