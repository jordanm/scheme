from scheme.util import *
from tests.util import *

class TestUtil(TestCase):
    def test_identify_object(self):
        import scheme
        self.assertEqual(identify_object(scheme), 'scheme')
        self.assertEqual(identify_object(identify_object), 'scheme.util.identify_object')

    def test_minimize_string(self):
        for candidate in ('test this', 'test    this', '   test this', 'test this   ', '   test   this   '):
            self.assertEqual(minimize_string(candidate), 'test this')

    def test_pluralize(self):
        self.assertEqual(pluralize('life', 1), 'life')
        self.assertEqual(pluralize('life', 2), 'lives')

    def test_recursive_merge(self):
        original = {'one': {'two': {'three': True}, 'four': [1, 2, 3]}}
        merged = recursive_merge(original, {'one': {'two': {'five': False}, 'four': 1.2}, 'six': 'test'})

        self.assertIs(merged, original)
        self.assertEqual(merged, {'one': {'two': {'three': True, 'five': False}, 'four': 1.2}, 'six': 'test'})

    def test_set_nested_value(self):
        original = {'one': {'two': {'three': True}, 'four': [1, 2, 3]}}
        set_nested_value(original, 'one.two.three', False)
        self.assertEqual(original['one']['two']['three'], False)

        with self.assertRaises(KeyError):
            set_nested_value(original, 'one.five.three', True)

        with self.assertRaises(TypeError):
            set_nested_value(original, 'one.four.three', True)

    def test_traverse_to_key(self):
        original = {'one': {'two': {'three': True}, 'four': [1, 2, 3]}}
