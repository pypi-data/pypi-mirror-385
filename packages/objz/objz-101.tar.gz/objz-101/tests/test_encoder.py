# This file is placed in the Public Domain.


import unittest


from objz.objects import Object
from objz.serials import dumps


VALIDJSON = '{"test": "bla"}'


class TestEncoder(unittest.TestCase):

    def test_dumps(self):
        obj = Object()
        obj.test = "bla"
        self.assertEqual(dumps(obj), VALIDJSON)
