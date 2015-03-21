try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from scheme import *
from tests.util import *

class TestStructuredText(FormatTestCase):
    format = StructuredText

    def test_invalid_value(self):
        with self.assertRaises(ValueError):
            StructuredText.unserialize(True)

    def test_nulls(self):
        self.assert_correct([(None, 'null')])

    def test_booleans(self):
        self.assert_correct([(True, 'true'), (False, 'false')])
        self.assert_correct([(True, 'True'), (False, 'False')], test_serialize=False)

    def test_mappings(self):
        self.assert_correct([
            ({}, '{}'),
            ({'b': '1'}, '{b:1}'),
            ({'b': '1', 'c': '2'}, '{b:1,c:2}'),
            ({'b': True, 'c': False}, '{b:true,c:false}'),
            ({'b': 'a:b', 'c': 'a:c'}, '{b:a:b,c:a:c}'),
        ])
        self.assert_correct([({'b': 1, 'c': 2}, '{b:1,c:2}')], parse_numbers=True)

    def test_sequences(self):
        self.assert_correct([
            ([], '[]'),
            (['1'], '[1]'),
            (['1', '2'], '[1,2]'),
            ([True, False], '[true,false]'),
        ])
        self.assert_correct([([1, 2], '[1,2]')], parse_numbers=True)

    def test_nested_structures(self):
        self.assert_correct([
            ({'b': {}}, '{b:{}}'),
            (['1', '2', ['3', []]], '[1,2,[3,[]]]'),
            ([True, {'b': [False, '1']}], '[true,{b:[false,1]}]'),
        ])

    def test_parse_numbers(self):
        self.assert_correct([
            (1, '1'),
            ({'b': 1.2}, '{b:1.2}'),
        ], parse_numbers=True)

    def test_parsing_escape_characters(self):
        self.assert_correct([
            ('{', '\{'),
            ('}', '\}'),
            ('{}', '\{\}'),
            ('{a}', '\{a\}'),
        ])
        self.assert_correct([
            ('[', '\['),
            (']', '\]'),
            ('[]', '\[\]'),
            ('[a]', '\[a\]'),
        ])
        self.assert_correct([
            ({'b': '{}'}, '{b:\{\}}'),
            ({'b': '[]'}, '{b:\[\]}'),
            ({'a': '[]', 'b': '{}', 'c': '1', 'd': [], 'e': {}}, '{a:\[\],b:\{\},c:1,d:[],e:{}}'),
        ])
        self.assert_correct([
            (['{}'], '[\{\}]'),
            (['[]'], '[\[\]]'),
            (['{}', '[]', 'b', [], {}], '[\{\},\[\],b,[],{}]'),
        ])
        self.assert_correct([
            (r'\\', r'\\'),
            (r'\\b', r'\\b'),
        ])
