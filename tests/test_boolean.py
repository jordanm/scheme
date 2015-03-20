from scheme import *
from tests.util import *

class TestBoolean(FieldTestCase):
    def test_processing(self):
        field = Boolean()
        self.assert_processed(field, None, True, False)
        self.assert_not_processed(field, 'invalid', 1, '')

    def test_constants(self):
        field = Boolean(constant=True)
        self.assert_processed(field, True)
        self.assert_not_processed(field, 'invalid', False, '')

    def test_interpolation(self):
        field = Boolean()
        self.assert_interpolated(field, None, True, False)
        self.assert_interpolated(field, ('${value}', True), value=True)
