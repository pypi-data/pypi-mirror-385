# This file is placed in the Public Domain.


import unittest


from objz import Object, dumps, loads, update


class TestComposite(unittest.TestCase):

    def testcomposite(self):
        obj = Object()
        obj.obj = Object()
        obj.obj.a = "test"
        self.assertEqual(obj.obj.a, "test")

    def testcompositeprint(self):
        obj = Object()
        obj.obj = Object()
        obj.obj.a = "test"
        txt = dumps(obj)
        ooo = Object()
        update(ooo, loads(txt))
        self.assertTrue(ooo.obj)
