from itertools import product

from scheme import *
from tests.util import *

class TestEnumeration(FieldTestCase):
    def test_instantiation(self):
        field = Enumeration('alpha beta gamma', ignored_values='alpha beta')
        self.assertEqual(field.enumeration, ['alpha', 'beta', 'gamma'])
        self.assertEqual(field.ignored_values, ['alpha', 'beta'])

        for invalid_value in (True, [datetime.now()]):
            with self.assertRaises(TypeError):
                Enumeration(invalid_value)

        for invalid_ignored_value in (True, [datetime.now()]):
            with self.assertRaises(TypeError):
                Enumeration('alpha beta', ignored_values=invalid_ignored_value)

    def test_processing(self):
        values = ['alpha', 1, True]
        field = Enumeration(values)

        self.assert_processed(field, None, *values)
        self.assert_not_processed(field, 'invalid', 'beta', 2, False)

    def test_ignored_values(self):
        field = Enumeration('alpha beta', ignored_values='gamma delta')
        self.assert_processed(field, None, 'alpha', 'beta')
        self.assert_not_processed(field, 'invalid', 'epsilon', 'iota')

        for value, serialized in product(['gamma', 'delta'], [True, False]):
            self.assertEqual(field.process(value, INBOUND, serialized), None)

    def test_interpolation(self):
        field = Enumeration('alpha beta')
        self.assert_interpolated(field, None, 'alpha', 'beta')
        self.assert_interpolated(field, ('${value}', 'alpha'), value='alpha')

        with self.assertRaises(CannotInterpolateError):
            field.interpolate('', {})

    def test_redefine(self):
        field = Enumeration('alpha beta')
        self.assert_processed(field, None, 'alpha', 'beta')
        self.assert_not_processed(field, 'invalid', 'gamma', 'delta')

        field.redefine('gamma', strategy='append')
        self.assert_processed(field, None, 'alpha', 'beta', 'gamma')
        self.assert_not_processed(field, 'invalid', 'delta')

        field.redefine('beta gamma', strategy='append')
        self.assert_processed(field, None, 'alpha', 'beta', 'gamma')
        self.assert_not_processed(field, 'invalid', 'delta')

        field.redefine('beta gamma', strategy='replace')
        self.assert_processed(field, None, 'beta', 'gamma')
        self.assert_not_processed(field, 'invalid', 'alpha', 'delta')

        field.redefine(['delta'], strategy='append')
        self.assert_processed(field, None, 'beta', 'gamma', 'delta')
        self.assert_not_processed(field, 'invalid', 'alpha')

        with self.assertRaises(ValueError):
            field.redefine('epsilon', 'invalid')

