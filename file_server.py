import socket
import threadpool
import os
import file_server_model

server_thread_pool = threadpool.ThreadPool(500)
port_number = 8080
ip_address = socket.gethostbyname(socket.gethostname())
file_system_manager = file_server_model.FileSystemManager('FileSystemDirectory')

def create_server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', port_number)
    print('Starting up on %s port %s' % server_address)
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
                connection.sendall('Killing Service\n')
                connection.close()
                os._exit(0)

            elif split_data[0] == 'ls':
                if len(split_data) == 1:
                    response = file_system_manager.list_directory_contents(client_id) + '\n'
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'cd':
                if len(split_data) == 2:
                    response = file_system_manager.change_directory(split_data[1], client_id)
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'up':
                if len(split_data) == 1:
                    response = file_system_manager.move_up_directory(client_id)
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'read':
                if len(split_data) == 2:
                    response = file_system_manager.read_item(client_id, split_data[1])
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'write':
                if len(split_data) == 3:
                    response = file_system_manager.write_item(client_id, split_data[1], split_data[2])
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'delete':
                if len(split_data) == 2:
                    response = file_system_manager.delete_file(client_id, split_data[1])
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'lock':
                if len(split_data) == 2:
                    client = file_system_manager.get_active_client(client_id)
                    res = file_system_manager.lock_item(client, split_data[1])
                    response = ''
                    if res == 0:
                        response = 'File locked\n'
                    elif res == 1:
                        response = 'File already locked\n'
                    elif res == 2:
                        response = 'File does not exist\n'
                    elif res == 3:
                        response = 'Locking directories is not supported\n'
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'release':
                if len(split_data) == 2:
                    client = file_system_manager.get_active_client(client_id)
                    response = file_system_manager.release_item(client, split_data[1])
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'mkdir':
                if len(split_data) == 2:
                    response = file_system_manager.make_directory(client_id, split_data[1])
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'rmdir':
                if len(split_data) == 2:
                    response = file_system_manager.remove_directory(client_id, split_data[1])
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

            elif split_data[0] == 'pwd':
                if len(split_data) == 1:
                    response = file_system_manager.get_working_dir(client_id) + '\n'
                    connection.sendall(response.encode())
                else:
                    error_response(connection, 1)

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
    response = ''
    if error_code == 0:
        response = 'Server error\n'
    if error_code == 1:
        response = 'Unrecognised command\n'
    connection.sendall(response.encode())

if __name__ == '__main__':
    create_server_socket()
    server_thread_pool.wait_completion()
