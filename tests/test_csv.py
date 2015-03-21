from scheme import *
from tests.util import *

SCHEMA = Sequence(Structure({
    'alpha': Text(),
    'beta': Boolean(),
    'gamma': Integer(),
    'delta': Tuple((Integer(), Text())),
}))

DATA = [
    {'alpha': 'testing', 'beta': True, 'gamma': 12, 'delta': (1, '1')},
    {'alpha': 'more', 'beta': False, 'gamma': 14},
    {'alpha': 'less', 'gamma': None},
]

SERIALIZED = '''"alpha","beta","gamma"\r
"testing","true","12"\r
"more","false","14"\r
"less","",""\r
'''

UNSERIALIZED = [
    {'alpha': 'testing', 'beta': True, 'gamma': 12},
    {'alpha': 'more', 'beta': False, 'gamma': 14},
    {'alpha': 'less'},
]

class TestCsv(FormatTestCase):
    format = Csv

    def test_format(self):
        self.assertEqual(Csv.serialize(DATA, SCHEMA), SERIALIZED)
        self.assertEqual(Csv.unserialize(SERIALIZED, SCHEMA), UNSERIALIZED)
