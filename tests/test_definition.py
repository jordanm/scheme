from scheme import *
from tests.util import *

class TestDefinition(FieldTestCase):
    def test_construction(self):
        with self.assertRaises(TypeError):
            Definition(True)

        with self.assertRaises(ValueError):
            Definition([True])

        field = Definition(valid_fields='text integer')
        self.assertEqual(field.valid_fields, ('text', 'integer'))

    def test_processing(self):
        field = Definition()
        self.assert_processed(field, None)
        self.assert_not_processed(field, 'invalid', True)

        serialized = field.process(Text(name='test', required=True), OUTBOUND, True)
        self.assertIsInstance(serialized, dict)
        self.assertEqual(serialized, {'fieldtype': 'text', 'name': 'test', 'required': True})

        unserialized = field.process(serialized, INBOUND, True)
        self.assertIsInstance(unserialized, Text)
        self.assertEqual(unserialized.name, 'test')
        self.assertTrue(unserialized.required)

    def test_valid_fields(self):
        field = Definition('integer text')
        self.assert_processed(field, None)
        self.assert_not_processed(field, 'invalid', True)

        serialized = field.process(Text(name='test', required=True), OUTBOUND, True)
        self.assertIsInstance(serialized, dict)
        self.assertEqual(serialized, {'fieldtype': 'text', 'name': 'test', 'required': True})

        self.assert_not_processed(field, 'invalidfield', Boolean(name='test'))
