from scheme import *
from tests.util import *

VALID_UUID = '9ddfe7e5-79b4-4179-8993-43f304d6b012'
SHORT_UUID = '9ddfe7e5-79b4-4179-8993-43f304d6b01'

class TestUUID(FieldTestCase):
    def test_processing(self):
        field = UUID()
        self.assert_processed(field, None, VALID_UUID)
        self.assert_not_processed(field, 'invalid', True, '', SHORT_UUID)

    def test_interpolation(self):
        field = UUID()
        self.assert_interpolated(field, None, VALID_UUID)
        self.assert_interpolated(field, ('${value}', VALID_UUID), value=VALID_UUID)
