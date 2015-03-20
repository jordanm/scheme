from scheme import *
from tests.util import *

class TestEmail(FieldTestCase):
    def test_invalid_instantiation(self):
        with self.assertRaises(ValueError):
            Email(multiple=True, extended=True)

    def test_single_nonextended(self):
        field = Email()
        self.assert_processed(field, None, '', 'test@test.com')
        self.assertEqual(field.process('TEST@test.com'), 'test@test.com')
        self.assert_not_processed(field, 'invalid', True)
        self.assert_not_processed(field, 'pattern', 'not an email')

    def test_multiple_nonextended(self):
        field = Email(multiple=True)
        self.assert_processed(field, None, '', 'test@test.com', 'test@test.com,more@test.com')
        self.assertEqual(field.process('TEST@test.com more@TEST.com;some@test.com'),
            'test@test.com,more@test.com,some@test.com')

    def test_extended(self):
        field = Email(extended=True)
        self.assert_processed(field, None, '', 'test@test.com', 'Test <test@test.com>',
            '"Test User" <test@test.com>')
