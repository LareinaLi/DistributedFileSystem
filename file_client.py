import socket
import threadpool
import time
import os

client_thread_pool = threadpool.ThreadPool(5)
ip_address = socket.gethostbyname(socket.gethostname())
port_num = 8080
response_var = ''

def connect_to_server_userin():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', port_num)
    print('Connecting to %s on port %s\n' % server_address)
    sock.connect(server_address)

    client_thread_pool.add_task(get_server_response, sock)

    while True:
        user_in = input()
        split_input = user_in.split(' ')
        if split_input[0] == 'write':
            try:
                file = open(split_input[1])
                file_contents = file.read()
                message = '%s////%s////%s' % (split_input[0], split_input[1], file_contents)
            except IOError:
                print('no such file in source directory\n')
                message = ''
        else:
            message = '////'.join(split_input)
        
        global response_var
        split_message = message.split('////')
        if len(split_message) == 2 and split_message[0] == 'read':
            connection.send('pwd')
            time.sleep(1)
            response_message = response_var
            search_term = '%s%s' % (response_message, split_message[1])
            print(search_term)
        else：
            sock.send(message.encode())
            if message == 'exit':
                os._exit(0)

def get_server_response(sock):
    global response_var
    while True:
        data = sock.recv(1024).decode()
        response_var = data
        if data is not None:
            if len(data.split('////')) == 2:
                split_data = data.split('////')
                print(split_data[1])
            else:
                print(data)

if __name__ == '__main__':
    connect_to_server_userin()
    client_thread_pool.wait_completion()
