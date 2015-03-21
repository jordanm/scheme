from datetime import date, datetime, time, timedelta
from inspect import getargspec
from uuid import uuid4

try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from scheme.exceptions import *
from scheme.field import *
from scheme.timezone import *
from scheme.util import string

def call_with_supported_params(callable, *args, **params):
    arguments = getargspec(callable)[0]
    for key in list(params):
        if key not in arguments:
            del params[key]
    return callable(*args, **params)

def construct_now(delta=None):
    now = datetime.now().replace(microsecond=0, tzinfo=LOCAL)
    if delta is not None:
        now += timedelta(seconds=delta)

    now_text = now.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')
    return now, now_text

def construct_today(delta=None):
    today = date.today()
    if delta is not None:
        today += timedelta(days=delta)

    return today, today.strftime('%Y-%m-%d')

def should_fail(callable, *args, **params):
    try:
        callable(*args, **params)
    except Exception as exception:
        return exception
    else:
        assert False, 'exception should be raised: %r(%r, %r)' % (callable, args, params)

class attrmap(object):
    def __init__(self, field, value, key=None):
        self.__dict__.update(value)

    @classmethod
    def extract(self, field, value):
        return value.__dict__

class listwrapper(object):
    def __init__(self, field, value, key=None):
        self.list = value

    @classmethod
    def extract(self, field, value):
        return value.list

class valuewrapper(object):
    def __init__(self, field, value, key=None):
        self.value = value

    @classmethod
    def extract(self, field, value):
        return value.value

INVALID_ERROR = ValidationError({'token': 'invalid'})
NULL_ERROR = ValidationError({'token': 'nonnull'})
REQUIRED_ERROR = ValidationError({'token': 'required'})
UNKNOWN_ERROR = ValidationError({'token': 'unknown'})

class FieldTestCase(TestCase):
    def assert_processed(self, field, *tests, **params):
        ancestry = params.get('ancestry', None)
        for test in tests:
            if isinstance(test, tuple):
                unserialized, serialized = test
            else:
                unserialized, serialized = (test, test)
            self.assertEqual(field.process(unserialized, INBOUND, ancestry=ancestry), unserialized)
            self.assertEqual(field.process(unserialized, OUTBOUND, ancestry=ancestry), unserialized)
            self.assertEqual(field.process(serialized, INBOUND, True, ancestry=ancestry), unserialized)
            self.assertEqual(field.process(unserialized, OUTBOUND, True, ancestry=ancestry), serialized)

    def assert_not_processed(self, field, expected, *tests):
        if isinstance(expected, string):
            expected = ValidationError().append({'token': expected})

        for test in tests:
            if not isinstance(test, tuple):
                test = (test, test)

            error = should_fail(field.process, test[0], INBOUND)
            failed, reason = self.compare_structural_errors(expected, error)
            assert failed, reason

            for value, phase in zip(test, (OUTBOUND, INBOUND)):
                error = should_fail(field.process, value, phase, True)
                failed, reason = self.compare_structural_errors(expected, error)
                assert failed, reason

    def assert_interpolated(self, field, *tests, **params):
        for test in tests:
            if isinstance(test, tuple):
                left, right = test
            else:
                left, right = test, test
            self.assertEqual(field.interpolate(left, params), right)

    def compare_structural_errors(self, expected, received):
        if not isinstance(received, type(expected)):
            return False, 'received error %r not expected type %r' % (received, type(expected))
        if not self.compare_errors(expected, received):
            return False, 'nonstructural errors do not match: %r, %r' % (expected.errors, received.errors)
        if not self.compare_structure(expected, received):
            return False, 'structural errors do not match: %r, %r' % (expected.structure, received.structure)
        return True, ''

    def compare_errors(self, expected, received):
        if expected.errors:
            if len(received.errors) != len(expected.errors):
                return False
            for expected_error, received_error in zip(expected.errors, received.errors):
                if received_error.get('token') != expected_error['token']:
                    return False
        elif received.errors:
            return False
        return True

    def compare_structure(self, expected, received):
        expected, received = expected.structure, received.structure
        if isinstance(expected, list):
            if not isinstance(received, list):
                return False
            elif len(received) != len(expected):
                return False
            for expected_item, received_item in zip(expected, received):
                if isinstance(expected_item, StructuralError):
                    if not isinstance(received_item, StructuralError):
                        return False
                    elif expected_item.structure is not None:
                        if not self.compare_structure(expected_item, received_item):
                            return False
                    elif expected_item.errors is not None:
                        if not self.compare_errors(expected_item, received_item):
                            return False
                elif received_item != expected_item:
                    return False
        elif isinstance(expected, dict):
            if not isinstance(received, dict):
                return False
            elif len(received) != len(expected):
                return False
            for expected_pair, received_pair in zip(sorted(expected.items()), sorted(received.items())):
                if expected_pair[0] != received_pair[0]:
                    return False
                expected_value, received_value = expected_pair[1], received_pair[1]
                if isinstance(expected_value, StructuralError):
                    if not isinstance(received_value, StructuralError):
                        return False
                    elif expected_value.structure is not None:
                        if not self.compare_structure(expected_value, received_value):
                            return False
                    elif expected_value.errors is not None:
                        if not self.compare_errors(expected_value, received_value):
                            return False
                elif received_value != expected_value:
                    return False
        elif received:
            return False
        return True

class FormatTestCase(TestCase):
    format = None

    def assert_correct(self, pairs, test_serialize=True, test_unserialize=True, **params):
        for unserialized, serialized in pairs:
            if test_serialize:
                self.assertEqual(call_with_supported_params(self.format.serialize,
                    unserialized, **params), serialized)
            if test_unserialize:
                self.assertEqual(call_with_supported_params(self.format.unserialize,
                    serialized, **params), unserialized)
