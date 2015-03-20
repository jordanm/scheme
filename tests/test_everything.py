import timeit
from cProfile import Profile

Environment = r'''
from datetime import date, datetime, time
from decimal import Decimal as decimal
from uuid import uuid4

from scheme import *

Schema = Structure({
    'id': UUID(nonempty=True),
    'binary': Binary(),
    'boolean': Boolean(),
    'date': Date(),
    'datetime': DateTime(),
    'decimal': Decimal(),
    'definition': Definition(),
    'email': Email(),
    'enumeration': Enumeration('one two'),
    'float': Float(),
    'integer': Integer(),
    'map': Map(Sequence(Text())),
    'object': Object(),
    'sequence': Sequence(Map(Text())),
    'structure': Structure({
        'alpha': {
            'numbers': Sequence(Integer()),
        },
        'beta': {
            'letters': Sequence(Text()),
        },
        '*': {
            'always': Boolean(),
        },
    }, polymorphic_on='type'),
    'surrogate': Surrogate(),
    'text': Text(minlength=5),
    'time': Time(),
    'token': Token(),
    'tuple': Tuple((Integer(), Text())),
})

UnprocessedData = {
    'id': 'fec5eadb-1de1-4102-86fb-e88e131086e3',
    #'binary': '\x00' * 1024,
    'boolean': True,
    'date': date(2000, 1, 1),
    'datetime': datetime(2000, 1, 1, 12, 0, 0, tzinfo=UTC),
    'decimal': decimal('1.0'),
    'email': 'test@test.com',
    'enumeration': 'one',
    'float': 1.0,
    'integer': 1,
    'map': {'a': ['a', 'a'], 'b': ['b', 'b']},
    'sequence': [{'a': 'a'}, {'b': 'b'}],
    'structure': {'type': 'alpha', 'always': True, 'numbers': [1, 2, 3]},
    'text': 'x' * 4096,
    'time': time(12, 0, 0),
    'token': 'token',
    'tuple': (12, '12'),
}

SerializedData = {
    'id': 'fec5eadb-1de1-4102-86fb-e88e131086e3',
    #'binary': ('A' * 1366) + '==',
    'boolean': True,
    'date': '2000-01-01',
    'datetime': '2000-01-01T12:00:00Z',
    'decimal': '1.0',
    'email': 'test@test.com',
    'enumeration': 'one',
    'float': 1.0,
    'integer': 1,
    'map': {'a': ['a', 'a'], 'b': ['b', 'b']},
    'sequence': [{'a': 'a'}, {'b': 'b'}],
    'structure': {'type': 'alpha', 'always': True, 'numbers': [1, 2, 3]},
    'text': 'x' * 4096,
    'time': '12:00:00',
    'token': 'token',
    'tuple': (12, '12'),
}

JsonData = """{
    "id": "fec5eadb-1de1-4102-86fb-e88e131086e3",
    "boolean": true,
    "date": "2000-01-01",
    "datetime": "2000-01-01T12:00:00Z",
    "decimal": "1.0",
    "email": "test@test.com",
    "enumeration": "one",
    "float": 1.0,
    "integer": 1,
    "map": {"a": ["a", "a"], "b": ["b", "b"]},
    "sequence": [{"a": "a"}, {"b": "b"}],
    "structure": {"type": "alpha", "always": true, "numbers": [1, 2, 3]},
    "text": "%s",
    "time": "12:00:00",
    "token": "token",
    "tuple": [12, "12"]
}""" % ('x' * 4096)
'''

def profile_while_timing(statement, setup=Environment, number=5000):
    profile = Profile()
    profile.enable()
    timeit.timeit(statement, setup, number=number)
    profile.disable()
    profile.print_stats('cumtime')

def profile_serialization():
    profile_while_timing("Schema.process(UnprocessedData, OUTBOUND, True)")

def profile_json_serialization():
    profile_while_timing("Schema.serialize(UnprocessedData, 'json')")

def profile_json_unserialization():
    profile_while_timing("Schema.unserialize(JsonData, 'json')")
