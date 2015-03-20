from scheme import *
from tests.util import *

class TestBinary(FieldTestCase):
    def test_construction(self):
        with self.assertRaises(TypeError):
            Binary(min_length='invalid')

        with self.assertRaises(TypeError):
            Binary(max_length='invalid')

        field = Binary(nonempty=True)
        self.assertTrue(field.required and field.nonnull
            and field.min_length == 1)

        field = Binary(nonempty=True, min_length=10)
        self.assertTrue(field.required and field.nonnull
            and field.min_length == 10)

    def test_processing(self):
        field = Binary()
        self.assert_processed(field, None, b'',
            (b'testing', b'dGVzdGluZw=='),
            (b'\x00\x00', b'AAA='))
        self.assert_not_processed(field, 'invalid', True, 1.0, u'')

    def test_min_length(self):
        field = Binary(min_length=1)
        self.assert_processed(field, (b'\x00', b'AA=='), (b'\x00\x00', b'AAA='), (b'\x00\x00\x00', b'AAAA'))
        self.assert_not_processed(field, 'min_length', (b'', b''))


        field = Binary(min_length=2)
        self.assert_processed(field, (b'\x00\x00', b'AAA='), (b'\x00\x00\x00', b'AAAA'))
        self.assert_not_processed(field, 'min_length', (b'', b''), (b'\x00', b'AA=='))

    def test_max_length(self):
        field = Binary(max_length=2)
        self.assert_processed(field, (b'', b''), (b'\x00', b'AA=='), (b'\x00\x00', b'AAA='))
        self.assert_not_processed(field, 'max_length', (b'\x00\x00\x00', b'AAAA'))

    def test_interpolation(self):
        field = Binary()
        self.assertEqual(field.interpolate(None, {}), None)
        self.assertEqual(field.interpolate(b'\x00\x01', {}), b'\x00\x01')
