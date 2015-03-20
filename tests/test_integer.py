from scheme import *
from tests.util import *

class TestInteger(FieldTestCase):
    def test_construction(self):
        with self.assertRaises(TypeError):
            Integer(minimum='bad')
        with self.assertRaises(TypeError):
            Integer(maximum='bad')

    def test_processing(self):
        field = Integer()
        self.assert_processed(field, None, -1, 0, 1)
        self.assert_not_processed(field, 'invalid', '')

    def test_minimum(self):
        field = Integer(minimum=0)
        self.assert_processed(field, 0, 1)
        self.assert_not_processed(field, 'minimum', -1)

    def test_maximum(self):
        field = Integer(maximum=0)
        self.assert_processed(field, -1, 0)
        self.assert_not_processed(field, 'maximum', 1)

    def test_minimum_maximum(self):
        field = Integer(minimum=-1, maximum=1)
        self.assert_processed(field, -1, 0, 1)
        self.assert_not_processed(field, 'minimum', -2)
        self.assert_not_processed(field, 'maximum', 2)

    def test_interpolation(self):
        field = Integer()
        self.assert_interpolated(field, None, 1, (1, 1.0))
        self.assert_interpolated(field, ('${value}', 1), ('${value + 1}', 2),
            value=1)
