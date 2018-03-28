"""
Item 36: Use subprocess to Manage Child Processes.
"""
import subprocess
import time
import sys

def run_sleep(period):
    proc = subprocess.Popen(['sleep', str(period)])
    return proc

def test_parallel():
    """ Test running procs in parallel by decoupling the parent process from
    child processes.
    
    Examples
    --------
    # This shows that the processes ran in parallel instead of in sequence
    >>> from py_learn.effective_python.thread import test_parallel
    >>> test_parallel()
    Finished 10 sleep 0.1 processes in 0.110 seconds

    """
    sys.stderr.write('Start running 10 procs of "sleep 0.1"\n')
    start = time.time()
    procs = []
    for _ in range(10):
        proc = run_sleep(0.1)
        procs.append(proc)
        
    # Wait for them to finish their I/O and terminate with the communicate method
    for proc in procs:
        proc.communicate()
    end = time.time()
    print('Finished 10 sleep 0.1 processes in %.3f seconds' % (end-start))
    
if __name__ == '__main__':
    sys.exit(test_parallel())