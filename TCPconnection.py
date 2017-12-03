"""
TCPconnection.py
@author: Lareina
"""
class Connection:

    def __init__(self, conn):
        self._conn = conn

    def send(self, data):
        self._conn.send(data)

    def close(self):
        self._conn.close()

    def shutdown(self, method):
        self._conn.shutdown(method)

class TCPServer(object):

    _host = "0.0.0.0"

    def __init__(self, port):
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self._bind()
        while True:
            v = self.get()
            conn, addr = v
            conn_obj = Connection(conn)
            t = threading.Thread(target=self._listen, args=())
            t.daemon = True
            t.start()

    def stop(self):
        for _ in range(self._threads):
            self._queue.put(None)

    def _bind(self):
        try:
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((self._host, self._port))
        except socket.error as err:
            raise Exception("Error " + str(err[0]) + ", bind failed: " + err[1])

    def _listen(self):
        self._socket.listen(10)
        while True:
            conn, addr = self._socket.accept()
            self._queue.put((conn, addr), False)       
