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
        
        # if use cache, replace these two sentences with next 8 sentences.
        if message == "exit":
            os._exit(0)
        # cache_res = cache_interaction(sock, message)
        # # if there is no cached response
        # if cache_res is None:
        #     sock.send(message.encode())
        #     if message == "exit":
        #         os._exit(0)
        # else:
        #     print(cache_res)

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

# def cache_interaction(connection, message):
#     global response_var
#     split_message = message.split('////')
#     if len(split_message) == 2 and split_message[0] == 'read':
#         connection.send('pwd')
#         time.sleep(1)
#         search_term = response_var + split_message[1]
#         return_message = search_cache(str(search_term))
#         if return_message is not None:
#             log_cache()
#             print(search_term)
#             return return_message
#         else:
#             return None
#     return None


# searches the cache for an item
# def search_cache(path):
#     for item in cache_queue:
#         if item[0] == path:
#             return item[1]
#     return None

# logs the contents of the cache
# def log_cache():
#     for item in cache_queue:
#         print('%s\t%s\t%d' % item)

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
