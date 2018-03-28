'''
What happens when __new__ method is patched with mock?
'''
import os
import sys
import unittest
from unittest.mock import patch


class AWithNew(object):
    def __new__(cls, *args, **kwargs):
        print('AWithNew.__new__ called with args=%s kwargs=%s' % (args, kwargs))
        return super().__new__(cls)

    def __init__(self, a=1, b=2):
        self.a = a
        self.b = b
        print('AWithNew.__init__ called')
        
class AWoNew(object):
    def __init__(self, a=1, b=2):
        print('AWoNew.__init__')
        self.a = a
        self.b = b
        print('AWoNew.__init__ called with self=%s, a=%s, b=%s' % (self, a, b))
        
class B(object):
    def __init__(self):
        self.AWithNew = AWithNew(a=3)
        self.AWoNew = AWoNew(a=2)
        print('B.__init__ called')

# import pdb
# pdb.set_trace()
print('\nBefore patch')
AWoNew.__new__(AWoNew)
AWoNew.__new__(AWoNew,a=1,b=2)
AWoNew(a=4, b=2)
print('AWoNew.__init__: %s' % AWoNew.__init__)
 
# with patch.object(A1, '__new__', spec=A1):
#     A1()
#     B()
#     print('A1.__init__: %s' % A1.__init__)

print('\npatching')
class Test1(unittest.TestCase):
    @patch.object(AWoNew, '__new__')
    def test_a(self, mock_new):
        print(AWoNew().a)

# unittest.main(exit=False)
print('\nAfter patching')
print('AWoNew.__init__: %s' % AWoNew.__init__)
a = AWoNew.__new__(AWoNew)
AWoNew.__init__(a, b =2)
try:
    AWoNew(a=4, b=2)
    print(B().AWoNew.a)
except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)
    raise