import datetime
import threadpool
import time
import os
import shutil


class Client:
    def __init__(self, id, socket, path_to_root):
        self.id = id
        self.socket = socket
        self.dir_level = 0
        self.dir_path = [path_to_root]

    def change_directory(self, dir_name):
        self.dir_level = self.dir_level + 1
        self.dir_path.append(dir_name)
        
    def move_up_directory(self):
        if self.dir_level > 0:
            self.dir_path.pop()
            self.dir_level = self.dir_level - 1
            return 'Have moved back to up directory\n'
        else:
            return 'Can not move up\n'

class FileSystemManager:
    active_clients = []
    next_client_id = 0
    next_event_id = 0
    events = []
    locked_files = []
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
        connection.sendall('Disconnected\n')
        connection.close()
        self.add_event('Disconnect client: %d' % client_id)

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

    def change_directory(self, dir_name, client_id):
        client = self.get_active_client(client_id)
        new_dir_path = self.resolve_path(client_id, dir_name)
        is_dir_val = os.path.isdir('./' + new_dir_path)
        if not is_dir_val:
            return 'Directory [' + dir_name + '] does not exist\n'
        client.change_directory(dir_name)
        self.update_client(client)
        self.add_event('cd ' + dir_name)
        return 'Changed directory to [' + dir_name + ']\n'

    def move_up_directory(self, client_id):
        client = self.get_active_client(client_id)
        result = client.move_up_directory()
        self.update_client(client)
        self.add_event('up')
        return result

    def list_directory_contents(self, client_id, item_name=''):
        path = self.resolve_path(client_id, item_name)
        item_type = self.item_exists(client_id, item_name)
        if item_type == -1:
            return 'No such directory %s' % item_name
        elif item_type == 0:
            return 'Cannot list contents of %s' % item_name
        else:
            item_list = os.listdir('./' + path)
            return_string = 'Type\tPath'
            for item in item_list:
                list_item_type = self.item_exists(client_id, item)
                if list_item_type == 0:
                    return_string = return_string + '\n' + 'f\t' + item
                elif list_item_type == 1:
                    return_string = return_string + '\n' + 'd\t' + item
            return return_string

    def resolve_path(self, client_id, item_name):
        client = self.get_active_client(client_id)
        file_path = ''
        for path_element in client.dir_path:
            file_path = file_path + '%s/' % path_element
        file_path = file_path + item_name
        return file_path

    def get_working_dir(self, client_id):
        file_path = ''
        client = self.get_active_client(client_id)
        for path_element in client.dir_path:
            file_path = path_element + '/'
        return file_path

    def lock_item(self, client, item_name):
        file_path = self.resolve_path(client.id, item_name)
        item_type = self.item_exists(client.id, item_name)
        if item_type == -1:
            return 2
        elif item_type == 1:
            return 3
        if self.check_lock(client, item_name):
            return 1
        else:
            lock_timestamp = datetime.datetime.now()
            lock_record = (client.id, lock_timestamp, file_path)
            self.locked_files.append(lock_record)
            self.add_event('lock ' + file_path)
            return 0

    def release_item(self, client, item_name):
        file_path = self.resolve_path(client.id, item_name)
        i = 0
        item_released = False
        for locked_file in self.locked_files:
            if file_path == locked_file[2]:
                if client.id == locked_file[0]:
                    self.locked_files.pop(i)
                    self.add_event('release ' + file_path)
                    item_released = True
            i = i + 1
        if item_released:
            return item_name + ' released\n'
        else:
            return 'You do not hold the lock for ' + item_name + '\n'

    def check_lock(self, client, item_name):
        file_path = self.resolve_path(client.id, item_name)
        for locked_file in self.locked_files:
            if locked_file[2] == file_path:
                return True
        return False

    def auto_release(self):
        while True:
            time.sleep(60)
            new_locked_file_list = []
            for locked_file in self.locked_files:
                for client in self.active_clients:
                    if locked_file[0] == client.id:
                        new_locked_file_list.append(locked_file)
            self.locked_files = new_locked_file_list
            self.add_event('lock auto-release')

    def log_locks(self):
        print('LID\tTIME\t\t\t\tPATH')
        for locked_file in self.locked_files:
            print('%d\t%s\t%s' % locked_file)

    def item_exists(self, client_id, item_name):
        file_path = self.resolve_path(client_id, item_name)
        is_file = os.path.isfile('./' + file_path)
        if is_file:
            return 0
        else:
            is_dir = os.path.isdir('./' + file_path)
            if is_dir:
                return 1
            else:
                return -1

    def read_item(self, client_id, item_name):
        item_type = self.item_exists(client_id, item_name)
        if item_type == -1:
            return item_name + ' does not exist\n'
        elif item_type == 1:
            return item_name + ' is a directory\n'
        elif item_type == 0:
            file_path = self.resolve_path(client_id, item_name)
            file = open(file_path)
            file_contents = file.read()
            self.add_event('read ' + file_path)
            return_string = '%s////%s\n' % (file_path, file_contents)
            return return_string

    def write_item(self, client_id, item_name, file_contents):
        item_type = self.item_exists(client_id, item_name)
        if item_type == 1:
            return 'Cannot write to a directory file\n'
        client = self.get_active_client(client_id)
        lock_res = self.lock_item(client, item_name)
        file_path = self.resolve_path(client_id, item_name)
        if lock_res == 1:
            return 'File locked\n'
        elif lock_res == 2:
            file = open(file_path, 'w+')
        else:
            file = open(file_path, 'a')
        file.truncate()
        file.write(file_contents)
        file.close()
        self.add_event('write ' + file_path)
        self.release_item(client, item_name)
        return 'Write successfull\n'

    def delete_file(self, client_id, item_name):
        item_type = self.item_exists(client_id, item_name)
        if item_type == -1:
            return 'File does not exist\n'
        if item_type == 1:
            return 'Use rmdir to delete a directory\n'
        client = self.get_active_client(client_id)
        lock_res = self.lock_item(client, item_name)
        if lock_res == 1:
            return 'File locked\n'
        file_path = self.resolve_path(client_id, item_name)
        os.remove(file_path)
        self.add_event('delete ' + file_path)
        self.release_item(client, item_name)
        return 'Delete successfull\n'

    def make_directory(self, client_id, directory_name):
        path = self.resolve_path(client_id, directory_name)
        exists = self.item_exists(client_id, directory_name)
        if exists == 0:
            return 'File of same name exists\n'
        elif exists == 1:
            return 'Directory of same name exists\n'
        elif -1:
            os.makedirs(path)
            self.add_event('mkdir ' + path)
            return 'New directory [' + directory_name + '] created\n'

    def remove_directory(self, client_id, directory_name):
        path = self.resolve_path(client_id, directory_name)
        item_type = self.item_exists(client_id, directory_name)
        if item_type == -1:
            return 'Directory [' + directory_name + '] does not exist\n'
        elif item_type == 0:
            return '[' + directory_name + '] is a file\n'
        elif item_type == 1:
            directory_has_locked_elements = False
            for lock_record in self.locked_files:
                if lock_record[2][0:len(path)] == path:
                    directory_has_locked_elements = True
            if directory_has_locked_elements:
                return 'Directory has locked contents\n'
            else:
                shutil.rmtree(path)
                self.add_event('rmdir ' + path)
                return 'Directory [' + directory_name + '] removed\n'
