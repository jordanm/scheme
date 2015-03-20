from datetime import date, datetime
from scheme import *
from tests.util import *

SINGLE_DICT = """a: 1
b: true
c: something"""

DICT_WITHIN_DICT = """a:
  b: 1
  c: true
d:
  e: 2
  f: false"""

SINGLE_LIST = "[1, 2, 3]"

LIST_WITHIN_LIST = """- [1, 2]
- [3, 4]"""

DICT_WITHIN_LIST = """- a: 1
  b: true
- a: 2
  b: false"""

LIST_WITHIN_DICT = """a: [1, 2]
b: [3, 4]"""

BLOCK_TEXT = """this is some block text that contains newlines, and
therefore should trigger the newline processing of yaml serialization, and
it would be rather disappointing if it doesn't"""

class TestYaml(FormatTestCase):
    format = Yaml

    def test_simple_values(self):
        self.assert_correct([
            (None, 'null'),
            (True, 'true'),
            (False, 'false'),
            (1, '1'),
            (1.0, '1.0'),
            (date(2000, 1, 1), '2000-01-01'),
            (datetime(2000, 1, 1, 0, 0, 0), '2000-01-01 00:00:00'),
        ])

        with self.assertRaises(ValueError):
            Yaml.serialize(object())

    def test_required_quotes(self):
        self.assert_correct([
            ('', "''"),
            ("'", "''''"),
            ('null', "'null'"),
            ('Null', "'Null'"),
            ('NULL', "'NULL'"),
            ('~', "'~'"),
            ('true', "'true'"),
            ('True', "'True'"),
            ('TRUE', "'TRUE'"),
            ('false', "'false'"),
            ('False', "'False'"),
            ('FALSE', "'FALSE'"),
            ('test: this', "'test: this'"),
        ])

    def test_empty_values(self):
        self.assert_correct([
            ({}, '{}'),
            ([], '[]'),
        ])
        self.assert_correct([
            (set(), '[]'),
            ((), '[]'),
        ], test_unserialize=False)

    def test_strings(self):
        self.assert_correct([
            ('short string', "short string"),
        ])

    def test_complex_values(self):
        self.assert_correct([
            ({'a': 1, 'b': True, 'c': 'something'}, SINGLE_DICT),
            ({'a': {'b': 1, 'c': True}, 'd': {'e': 2, 'f': False}}, DICT_WITHIN_DICT),
            ([1, 2, 3], SINGLE_LIST),
            ([[1, 2], [3, 4]], LIST_WITHIN_LIST),
            ([{'a': 1, 'b': True}, {'a': 2, 'b': False}], DICT_WITHIN_LIST),
            ({'a': [1, 2], 'b': [3, 4]}, LIST_WITHIN_DICT),
        ])
