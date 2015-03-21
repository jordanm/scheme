try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from scheme.interpolation import UndefinedParameterError, interpolate_parameters

class TestInterpolation(TestCase):
    def test_template_interpolation(self):
        result = interpolate_parameters('${alpha}', {'alpha': 1, 'beta': 2})
        self.assertEqual(result, '1')

        result = interpolate_parameters('${alpha} - ${beta}', {'alpha': 1, 'beta': 2})
        self.assertEqual(result, '1 - 2')

        result = interpolate_parameters('${alpha}', {'beta': 2})
        self.assertEqual(result, '')

        result = interpolate_parameters('', {'beta': 2})
        self.assertEqual(result, '')

        with self.assertRaises(ValueError):
            interpolate_parameters(True, {})

    def test_simple_interpolation(self):
        result = interpolate_parameters('${alpha}', {'alpha': 1, 'beta': 2}, True)
        self.assertEqual(result, 1)

        result = interpolate_parameters('${alpha}', {'alpha': '1', 'beta': '2'}, True)
        self.assertEqual(result, '1')
