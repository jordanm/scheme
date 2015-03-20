from scheme import *
from scheme.util import string
from tests.util import *

class TestObject(FieldTestCase):
    def test_processing(self):
        field = Object()
        self.assert_processed(field, None)
        self.assertEqual(field.process('tests.util.attrmap', OUTBOUND, True), 'tests.util.attrmap')
        self.assertIs(field.process(attrmap, INBOUND, True), attrmap)

        serialized = field.process(attrmap, OUTBOUND, True)
        self.assertIsInstance(serialized, string)
        self.assertEqual(serialized, 'tests.util.attrmap')

        unserialized = field.process(serialized, INBOUND, True)
        self.assertIs(unserialized, attrmap)

        with self.assertRaises(InvalidTypeError):
            field.process(object(), OUTBOUND, True)
        with self.assertRaises(ValidationError):
            field.process('does.not.exist', INBOUND, True)
