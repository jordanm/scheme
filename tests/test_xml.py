from scheme import *
from tests.util import *

SCHEMA = Structure({
    'alpha': Text(),
    'beta': Boolean(),
    'gamma': Date(),
    'delta': Sequence(Structure({'a': Integer(), 'b': Integer()}, name='v')),
    'epsilon': Map(Text()),
    'zeta': Tuple((Text(), Boolean())),
    'eta': Text(),
}, name='struct')

DATA = {'alpha': 'testing', 'beta': True, 'gamma': '2000-01-01',
    'delta': [{'a': 2, 'b': 4}, {'a': 6, 'b': 8}],
    'epsilon': {'a': '1', 'b': '2', 'c': '3'},
    'zeta': ('test', False), 'eta': None}

SERIALIZED = '<?xml version="1.0"?><struct><alpha>testing</alpha><beta>true</beta><delta><v><a>2</a><b>4</b></v><v><a>6</a><b>8</b></v></delta><epsilon><a>1</a><b>2</b><c>3</c></epsilon><eta null="true" /><gamma>2000-01-01</gamma><zeta><value>test</value><value>false</value></zeta></struct>'

class TestXml(FormatTestCase):
    format = Xml

    def test_format(self):
        self.assert_correct([(True, '<_>true</_>'), (False, '<_>false</_>')],
            schema=Boolean(name='_'), preamble=False)
        self.assert_correct([(DATA, SERIALIZED)], schema=SCHEMA)
