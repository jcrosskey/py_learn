"""
Item 37: Use Threads for Blocking I/O, Avoid for Parallelism.

Python enforces coherence with a mechanism called the "global interpreter lock" (GIL).
It is a mutual-exclusion lock that prevents CPython from being affected by preemptive multithreading,
where one thread takes control of a program by interrupting another thread.

Although Python supports multiple threads of execution, the GIL causes only one of them to make
forward progress at a time.
"""
from threading import Thread
from time import time
import select


numbers = [2139079, 1214759, 1516637, 1852285]

def factorize(number):
    for i in range(1, number + 1):
        if number % i == 0:
            yield i
            
class FactorizeThread(Thread):
    def __init__(self, number):
        self._number = number
        super().__init__()
    def run(self):
        self._factors = list(factorize(self._number))

def factorize_serial():
    start = time()
    for number in numbers:
        list(factorize(number))
    end = time()
    print(f'Serial factorize took {end-start:.3f} seconds')
    
def factorize_threads():
    start = time()
    threads = []
    for number in numbers:
        thread = FactorizeThread(number)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    end = time()
    print(f'4 threads factorize took {end-start:.3f} seconds')


def slow_systemcall():
    select.select([], [], [], 0.1)
    
def run_slow_system_call():
    """
    Use Python threads to make multiple system calls in parallel. This allows one
    to do blocking I/O at the same time as computation.
    """
    start = time()
    for _ in range(5):
        slow_systemcall()
    end = time()
    print(f'5 slow system calls in serial took {end-start:.3f} seconds')
    threads = []

    start = time()
    for _ in range(5):
        thread = Thread(target=slow_systemcall)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    end = time()
    print(f'5 slow system calls with threads took {end-start:.3f} seconds')
    
if __name__ == '__main__':
    print(f'Factorize {numbers}')
    factorize_serial()
    factorize_threads()
    run_slow_system_call()
    