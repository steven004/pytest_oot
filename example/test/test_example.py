__author__ = 'Steven LI'

from .testbed import *

def test_NumBase_add():
    ret = num1.add(3,4,5,6)
    assert ret == 23

def test_NumBase_mul():
    ret = num1.multiple(2,4,5)
    assert ret == 100, "result is not 100"

def test_NumChange():
    ret = num2.add(3,4,5,6)
    assert ret == 23
    ret = num2.multiple(4,5)
    assert ret == 460

def test_NumChange3():
    ret = num3.add(3,4,5,6)
    assert ret == 100
