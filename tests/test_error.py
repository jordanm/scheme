from scheme import *
from tests.util import *

class TestError(FieldTestCase):
    def test_processing(self):
        field = Error()
        self.assert_processed(field, None)
        self.assert_not_processed(field, 'invalid', True)

        error = StructuralError({'token': 'field'})
        self.assertEqual(field.process(error, OUTBOUND, True), ([{'token': 'field'}], None))
        self.assertIs(field.process(error, INBOUND, True), error)

        error = field.process(([{'token': 'field'}], None), INBOUND, True)
        self.assertIsInstance(error, StructuralError)
        self.assertEqual(error.errors, [{'token': 'field'}])
