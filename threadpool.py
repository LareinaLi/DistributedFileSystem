# Copy from http://code.activestate.com/recipes/577187-python-thread-pool/

import queue
from threading import Thread
from random import randrange
from time import sleep


class Worker(Thread):
    # Thread executing tasks from a given tasks queue
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:
                func(*args, **kargs)
            except Exception as e:
                print(e)
            self.tasks.task_done()


class ThreadPool:
    # Pool of threads consuming tasks from a queue

    def __init__(self, num_threads):
        self.tasks = queue.Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        # Add a task to the queue
        self.tasks.put((func, args, kargs))

    def wait_completion(self):
        # Wait for completion of all the tasks in the queue
        self.tasks.join()


if __name__ == '__main__':

    delays = [randrange(1, 10) for i in range(100)]

    def wait_delay(delaytime):
        print('sleeping for', delaytime, 'sec')
        sleep(delaytime)

    # 1) Init a Thread pool with the desired number of threads
    pool = ThreadPool(20)

    for i, d in enumerate(delays):
        # print the percentage of tasks placed in the queue
        print('%.2f%c' % ((float(i) / float(len(delays))) * 100.0, '%'))

        # 2) Add the task to the queue
        pool.add_task(wait_delay, d)

    # 3) Wait for completion
    pool.wait_completion()
