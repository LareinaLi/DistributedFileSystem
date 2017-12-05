import datetime
import threadpool
import time

class Client:
    def __init__(self, id, socket, path_to_root):
        self.id = id
        self.socket = socket
        self.dir_level = 0
        self.dir_path = [path_to_root]

class FileSystemManager:
    active_clients = []
    next_client_id = 0
    next_event_id = 0
    events = []
    file_system_manager_threadpool = threadpool.ThreadPool(1)

    def __init__(self, root_path):
        self.root_path = root_path
        self.file_system_manager_threadpool.add_task(self.auto_release)

    def gen_client_id(self):
        return_client_id = self.next_client_id
        self.next_client_id = self.next_client_id + 1
        return return_client_id

    def gen_event_id(self):
        return_event_id = self.next_event_id
        self.next_event_id = self.next_event_id + 1
        return return_event_id

    def add_client(self, connection):
        new_client_id = self.gen_client_id()
        new_client = Client(new_client_id, connection, self.root_path)
        self.active_clients.append(new_client)
        return new_client_id

    def remove_client(self, client_in):
        i = 0
        for client in self.active_clients:
            if client.id == client_in.id:
                self.active_clients.pop(i)
            i = i + 1

    def get_active_client(self, client_id):
        for client in self.active_clients:
            if client.id == client_id:
                return client

    def update_client(self, client_in):
        i = 0
        for client in self.active_clients:
            if client.id == client_in.id:
                self.active_clients[i] = client_in
            i = i + 1

    def client_exists(self, id_in):
        for client in self.active_clients:
            if client.id == id_in:
                return True
        return False

    def disconnect_client(self, connection, client_id):
        client = self.get_active_client(client_id)
        self.remove_client(client)
        connection.sendall('disconnected')
        connection.close()
        self.add_event('disconnect client %d' % client_id)

    def add_event(self, command):
        new_event_id = self.gen_event_id()
        event_timestamp = datetime.datetime.now()
        new_event_record = (new_event_id, command, event_timestamp)
        self.events.append(new_event_record)
        print('%d\t%s\t%s' % (new_event_record[0], new_event_record[2], new_event_record[1]))

    def log_events(self):
        print('EID\tTIME\t\t\t\tCOMMAND')
        for event in self.events:
            print('%d\t%s\t%s' % (event[0], event[2], event[1]))
