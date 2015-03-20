from scheme import *
from tests.util import *

class TestText(FieldTestCase):
    def test_construction(self):
        with self.assertRaises(TypeError):
            Text(min_length='bad')
        with self.assertRaises(TypeError):
            Text(max_length='bad')

        field = Text(nonempty=True)
        self.assertTrue(field.required and field.nonnull and field.min_length == 1)

        field = Text(nonempty=True, min_length=10)
        self.assertTrue(field.required and field.nonnull and field.min_length == 10)

    def test_processing(self):
        field = Text()
        self.assert_processed(field, None, '', 'testing')
        self.assert_not_processed(field, 'invalid', 4, True)

    def test_strip(self):
        field = Text()
        self.assertEqual(field.process('  '), '')

        field = Text(strip=False)
        self.assertEqual(field.process('  '), '  ')

    def test_pattern(self):
        field = Text(pattern=r'^[abc]*$')
        self.assert_processed(field, '', 'a', 'ab', 'bc', 'abc', 'aabbcc')
        self.assert_not_processed(field, 'pattern', 'q', 'aq')

    def test_min_length(self):
        field = Text(min_length=1)
        self.assert_processed(field, 'a', 'aa', 'aaa')
        self.assert_not_processed(field, 'min_length', '', '    ')

        field = Text(min_length=2)
        self.assert_processed(field, 'aa', 'aaa')
        self.assert_not_processed(field, 'min_length', '', 'a', '    ')

        field = Text(min_length=2, strip=False)
        self.assert_processed(field, 'aa', 'aaa', '   ')
        self.assert_not_processed(field, 'min_length', '', 'a')

    def test_max_length(self):
        field = Text(max_length=1)
        self.assert_processed(field, '', 'a')
        self.assert_not_processed(field, 'max_length', 'aa', 'aaa')

        field = Text(max_length=2)
        self.assert_processed(field, '', 'a', 'aa')
        self.assert_not_processed(field, 'max_length', 'aaa')

    def test_interpolation(self):
        field = Text()
        self.assert_interpolated(field, None, '', 'testing')
        self.assert_interpolated(field, ('${alpha}', 'one'), ('${beta}', 'two'),
            ('${alpha}, ${beta}', 'one, two'), alpha='one', beta='two')
