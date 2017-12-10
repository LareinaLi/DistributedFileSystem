import socket
import threadpool
import time
import os
import re

client_thread_pool = threadpool.ThreadPool(5)
ip_address = socket.gethostbyname(socket.gethostname())
port_num = 8080
cache_time = 2
cache_queue = []

def connect_to_server_userin():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('127.0.0.1', port_num)
    print('connecting to %s on port %s\n' % server_address)
    sock.connect(server_address)

    client_thread_pool.add_task(get_server_response, sock)
    client_thread_pool.add_task(auto_update_cache)

    while True:
        user_in = input()
        if re.match(r'write', user_in):
            split_input = user_in.split(' ', 2)
        else:
            split_input = user_in.split(' ')
        message = '////'.join(split_input)
        sock.send(message.encode())
        if message == "exit":
            os._exit(0)

def get_server_response(sock):
    while True:
        data = sock.recv(1024).decode()
        if data is not None:
            # if reading cache item
            if len(data.split('////')) == 2:
                split_data = data.split('////')
                add_to_cache(split_data[0], split_data[1])
                print(split_data[1])
            else:
                print(data)

# adds an item to the cache
def add_to_cache(path, contents):
    cache_queue.insert(0, (path, contents, 0))
    if len(cache_queue) > 5:
        cache_queue.pop()

# removes old items from cache
def auto_update_cache():
    global cache_queue
    while True:
        time.sleep(10)
        new_cache_queue = []
        for item in cache_queue:
            if item[2] < cache_time:
                new_cache_record = (item[0], item[1], item[2] + 1)
                new_cache_queue.append(new_cache_record)
        cache_queue = new_cache_queue


if __name__ == '__main__':
    connect_to_server_userin()
    client_thread_pool.wait_completion()
