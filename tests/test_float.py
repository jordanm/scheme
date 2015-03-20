from scheme import *
from tests.util import *

class TestFloat(FieldTestCase):
    def test_construction(self):
        with self.assertRaises(TypeError):
            Float(minimum=True)
        with self.assertRaises(TypeError):
            Float(maximum=True)

    def test_processing(self):
        field = Float()
        self.assert_processed(field, None, -1.0, -0.1, 0.0, 0.1, 1.0)
        self.assert_not_processed(field, 'invalid', '')

    def test_minimum(self):
        field = Float(minimum=0.0)
        self.assert_processed(field, 0.0, 0.1, 1.0)
        self.assert_not_processed(field, 'minimum', -1.0, -0.1)

    def test_maximum(self):
        field = Float(maximum=0.0)
        self.assert_processed(field, -1.0, -0.1, 0.0)
        self.assert_not_processed(field, 'maximum', 0.1, 1.0)

    def test_minimum_maximum(self):
        field = Float(minimum=-1.0, maximum=1.0)
        self.assert_processed(field, -1.0, -0.5, 0.0, 0.5, 1.0)
        self.assert_not_processed(field, 'minimum', -2.0, -1.1)
        self.assert_not_processed(field, 'maximum', 1.1, 2.0)

    def test_interpolation(self):
        field = Float()
        self.assert_interpolated(field, None, 1.0, (1, 1.0))
        self.assert_interpolated(field, ('${value}', 1.0), ('${value + 1}', 2.0),
            value=1.0)
