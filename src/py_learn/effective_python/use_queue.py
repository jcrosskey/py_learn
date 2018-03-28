"""
Item 39: Use Queue to Coordinate Work between Threads

Manage a pipeline of functions.
"""
import time
from queue import Queue
from _collections import deque
from threading import Lock, Thread


class MyQueue(object):
    def __init__(self):
        self.items = deque()
        self._lock = Lock()

    def put(self, item):
        with self._lock:
            self.items.append(item)

    def get(self):
        with self._lock:
            return self.items.popleft()


class Worker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0

    def run(self):
        while True:
            self.polled_count += 1
            try:
                item = self.in_queue.get()
            except IndexError:
                time.sleep(0.01)
            else:
                result = self.func(item)
                self.out_queue.put(result)
                self.work_done += 1


def run_manual_queue():
    download_q = MyQueue()
    resize_q = MyQueue()
    upload_q = MyQueue()
    done_q = MyQueue()
    threads = [Worker(lambda x: x, download_q, resize_q),
               Worker(lambda x: x*2, resize_q, upload_q),
               Worker(lambda x: x-1, upload_q, done_q)]

    for thread in threads:
        thread.start()

    for i in range(1000):
        download_q.put(i)

    while len(done_q.items) < 1000:
        time.sleep(1)

    processed = len(done_q.items)
    polled = sum(t.polled_count for t in threads)
    print(f'processed {processed} items after polling {polled} times')
    # this will wait in definitely, because of the infinite loop at line 34?


class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return
                yield item
            finally:
                self.task_done()


class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.polled_count = 0
        self.work_done = 0

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)


def run_Queue():
    download_q = ClosableQueue()
    resize_q = ClosableQueue()
    upload_q = ClosableQueue()
    done_q = ClosableQueue()
    threads = [StoppableWorker(lambda x: x, download_q, resize_q),
               StoppableWorker(lambda x: x*2, resize_q, upload_q),
               StoppableWorker(lambda x: x-1, upload_q, done_q)]

    for thread in threads:
        thread.start()

    for i in range(1000):
        download_q.put(i)
    download_q.close()
    download_q.join()
    resize_q.close()
    resize_q.join()
    upload_q.close()
    upload_q.join()
    print(f'{done_q.qsize()} items finished')


def queue_demo():
    in_queue = Queue()

    def consumer():
        print('Consumer waiting')
        in_queue.get()
        print('Consumer working')
        print('Consumer done')
        in_queue.task_done()
    Thread(target=consumer).start()
    print('Producer putting')
    in_queue.put(object())
    print('Producer waiting')
    in_queue.join()
    print('Producer done')


if __name__ == '__main__':
    queue_demo()
    run_Queue()
