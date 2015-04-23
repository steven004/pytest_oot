__author__ = 'Steven LI'

from .testbed import *
from test_steps import *

def test_NumBase_add_mulple():
    step("num1.add(3,4,5,6) == 23")
    step("num1.multiple(2,4,5) == 200")
    step("num4.add(3,4,5,6) == 23")

def test_NumBase_add_multiple2():
    steps('''
        num1.add(3,4,5,6) == 23
        num1.multiple(2,4,5) == 200
        num4.add(3,4,5,6) == 41
        ''')

def test_NumBase_add_multiple3():
    s('''
        num1.add(3,4,5,6) == 23
        num1.multiple(2,4,5) == 200
        num4.add(3,4,5,6) == 55
        ''')

def test_async1():
    s('''
        num_async.addw(var100, var100) == 100
        num_async.data_sync() -t 18
        num_async.get_value() == 300
        ''')

def test_async2():
    s('''
        num_async.addw(var100, var100) >= 300
        num_async.get_value() == 500 --repeat 20
        ''')