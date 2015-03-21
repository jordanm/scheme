try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from scheme import *
from tests.util import *

class TestUrlEncoded(FormatTestCase):
    format = UrlEncoded

    def test_invalid_value(self):
        with self.assertRaises(ValueError):
            UrlEncoded.serialize(True)

        with self.assertRaises(ValueError):
            UrlEncoded.unserialize(True)

    def test_nulls(self):
        self.assert_correct([({'a': None}, 'a=null')])

    def test_booleans(self):
        self.assert_correct([
            ({'a': True}, 'a=true'),
            ({'a': False}, 'a=false'),
        ])
        self.assert_correct([
            ({'a': True}, 'a=True'),
            ({'a': False}, 'a=False'),
        ], test_serialize=False)

    def test_structured_value(self):
        self.assert_correct([
            ({'a': {'b': True}}, 'a=%7Bb%3Atrue%7D'),
        ])
