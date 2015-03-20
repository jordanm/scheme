from decimal import Decimal as decimal

from scheme import *
from tests.util import *

class TestDecimal(FieldTestCase):
    def test_construction(self):
        for value in (True, '', 'test'):
            with self.assertRaises(TypeError):
                Decimal(minimum=value)

            with self.assertRaises(TypeError):
                Decimal(maximum=value)

    def test_processing(self):
        field = Decimal()
        self.assert_processed(field, None,
            (decimal('0'), '0'),
            (decimal('-1.0'), '-1.0'),
            (decimal('1'), '1'),
        )
        self.assert_not_processed(field, 'invalid', '')

    def test_minimum(self):
        field = Decimal(minimum='0.0')
        self.assert_processed(field,
            (decimal('0'), '0'),
            (decimal('0.0'), '0.0'),
            (decimal('1.0'), '1.0'),
        )
        self.assert_not_processed(field, 'minimum', decimal('-1.0'), decimal('-1'))

    def test_maximum(self):
        field = Decimal(maximum='0.0')
        self.assert_processed(field,
            (decimal('0'), '0'),
            (decimal('0.0'), '0.0'),
            (decimal('-1.0'), '-1.0'),
        )
        self.assert_not_processed(field, 'maximum', decimal('1.0'), decimal('1'))

    def test_interpolation(self):
        field = Decimal()
        self.assert_interpolated(field, None,
            ('1', decimal('1')),
            (decimal('1'), decimal('1')),
            ('1.0', decimal('1.0')),
        )
        self.assert_interpolated(field, ('${value}', decimal('1.0')), value=decimal('1.0'))
        self.assert_interpolated(field, ('${value}', decimal('1.0')), value='1.0')

    def test_description(self):
        field = Decimal(minimum='0.0')
        self.assertEqual(field.describe(), {'fieldtype': 'decimal', 'minimum': '0.0'})

        field = Decimal(maximum='0.0')
        self.assertEqual(field.describe(), {'fieldtype': 'decimal', 'maximum': '0.0'})

        field = Decimal(minimum='0.0', maximum='0.0')
        self.assertEqual(field.describe(), {'fieldtype': 'decimal', 'minimum': '0.0',
            'maximum': '0.0'})
