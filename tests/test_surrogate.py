from scheme import *
from scheme.surrogate import *
from tests.util import *

class TestSurrogate(TestCase):
    def test_construction(self):
        s = surrogate({'id': 'id', 'name': 'name'})
        self.assertIsInstance(s, surrogate)
        self.assertIsInstance(s, dict)
        self.assertEqual(s, {'id': 'id', 'name': 'name'})
        self.assertIsNone(s.schema)
        self.assertIsNone(s.version)
