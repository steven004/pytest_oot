__author__ = 'Steven LI'
import time

class Num_Base:
    def __init__(self, base=0):
        self.data = base

    def add(self, *args):
        ret_val = self.data
        for val in args:
            ret_val += val
        return ret_val

    def multiple(self, *args):
        ret_val = self.data
        for val in args:
            ret_val *= val
        return ret_val

class Num_Change:
    def __init__(self, base=0):
        self.data = base

    def add(self, *args):
        for val in args:
            self.data += val
        return self.data

    def multiple(self, *args):
        for val in args:
            self.data *= val
        return self.data

import random
class Num_Asyc(Num_Base):
    def addw(self, *args):
        self.data2 = self.data
        self.start = time.time()
        self.wait = True
        self.sleep = random.uniform(1, 20)
        print(self.sleep)
        for val in args:
            self.data2 += val
        #print(self.data2)
        return self.data

    def mulw(self, *args):
        self.data2 = self.data
        self.start = time.time()
        self.wait = True
        for val in args:
            self.data2 *= val
        #print(self.data2)
        return self.data

    def get_value(self):
        if self.wait:
            self.end = time.time()
            if self.end - self.start > self.sleep:
                self.data = self.data2
                self.wait = False

        return self.data

    def data_sync(self):
        if not self.wait: return
        while(True):
            self.end = time.time()
            if self.end - self.start > self.sleep:
                self.data = self.data2
                self.wait = False
                return
            time.sleep(1)

import sys
import threading
class KThread2(threading.Thread):
    """A subclass of threading.Thread, with a kill()
    method.

    Come from:
    Kill a thread in Python:
    http://mail.python.org/pipermail/python-list/2004-May/260937.html
    """

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run      # Force the Thread to install our trace.
        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the
        trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
          return self.localtrace
        else:
          return None

    def localtrace(self, frame, why, arg):
        if self.killed:
          if why == 'line':
            raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True

if __name__ == '__main__':
    num_1 = Num_Asyc(5)
    num_1.addw(3,4,5)

    null_list = ()
    num_1.data_sync(*null_list)
    print(num_1.get_value(*null_list))

    import threading
    #t = KThread2(target=num_1.data_sync)
    t = threading.Thread(target=num_1.data_sync)
    t.start()
    t.join(7)
    if t.is_alive():
        #t.kill()
        raise TimeoutError()
    print(num_1.get_value())
