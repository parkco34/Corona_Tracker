#!/usr/bin/env python
class TestClass(object):
    c = 299792458  #this is a class variable

    def __init__(self):
        self.e = 2.71 #instance variable

    def phiFunc(self):
        self.phi = 1.618 #will become an instance variable after phiFunc is called
        x=224 #this is a method variable and can't be accessed outside this method

assert TestClass.c == 299792458
try:
    print TestClass.e #Not defined
except AttributeError:
    pass

testInst = TestClass()
assert testInst.c == 299792458 #instance gets c, currently a ref to the class var
assert testInst.e == 2.71 #got e because of __init__
try:
    print testInst.phi #error since not defined yet
except AttributeError:
    pass

testInst.phiFunc()
assert testInst.phi == 1.618 #now its here
try:
    testInst.x #still undefined
except AttributeError:
    pass

