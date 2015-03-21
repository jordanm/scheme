import os
from tempfile import mkstemp

try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from scheme import *

class TestFormat(TestCase):
    def test_read_via_format(self):
        fileno, filename = mkstemp()
        os.write(fileno, b'{"attr": "value"}')
        os.close(fileno)

        try:
            value = Format.read(filename, 'json')
            self.assertEqual(value, {'attr': 'value'})
        finally:
            os.unlink(filename)

    def test_read_via_suffix(self):
        fileno, filename = mkstemp(suffix='.json')
        os.write(fileno, b'{"attr": "value"}')
        os.close(fileno)

        try:
            value = Format.read(filename)
            self.assertEqual(value, {'attr': 'value'})
        finally:
            os.unlink(filename)

    def test_read_via_class(self):
        fileno, filename = mkstemp()
        os.write(fileno, b'{"attr": "value"}')
        os.close(fileno)

        try:
            value = Json.read(filename)
            self.assertEqual(value, {'attr': 'value'})
        finally:
            os.unlink(filename)

    def test_invalid_read_path(self):
        with self.assertRaises(ValueError):
            Format.read('filename')

        self.assertFalse(Format.read('filename', quiet=True))

    def test_invalid_read_format(self):
        fileno, filename = mkstemp()
        os.close(fileno)

        try:
            with self.assertRaises(ValueError):
                Format.read(filename, 'invalid')
        finally:
            os.unlink(filename)

    def test_invalid_read_extension(self):
        fileno, filename = mkstemp()
        os.close(fileno)

        try:
            with self.assertRaises(ValueError):
                Format.read(filename)
        finally:
            os.unlink(filename)

    def test_serialize(self):
        self.assertEqual(Format.serialize('test', 'json'), '"test"')
        self.assertEqual(Format.serialize([1, 2, 3], 'yaml'), '[1, 2, 3]')

    def test_unserialize(self):
        self.assertEqual(Format.unserialize('"test"', 'json'), 'test')
        self.assertEqual(Format.unserialize('[1, 2, 3]', 'yaml'), [1, 2, 3])

    def test_write_via_format(self):
        fileno, filename = mkstemp()
        os.close(fileno)

        try:
            Format.write(filename, {'attr': 'value'}, 'json')
            with open(filename) as openfile:
                self.assertEqual(openfile.read(), '{"attr": "value"}')
        finally:
            os.unlink(filename)

    def test_write_via_suffix(self):
        fileno, filename = mkstemp(suffix='.json')
        os.close(fileno)

        try:
            Format.write(filename, {'attr': 'value'})
            with open(filename) as openfile:
                self.assertEqual(openfile.read(), '{"attr": "value"}')
        finally:
            os.unlink(filename)

    def test_write_via_class(self):
        fileno, filename = mkstemp()
        os.close(fileno)

        try:
            Json.write(filename, {'attr': 'value'})
            with open(filename) as openfile:
                self.assertEqual(openfile.read(), '{"attr": "value"}')
        finally:
            os.unlink(filename)

    def test_invalid_write_format(self):
        with self.assertRaises(ValueError):
            Format.write('filename', {'attr': 'value'}, 'invalid')

    def test_invalid_write_extension(self):
        with self.assertRaises(ValueError):
            Format.write('filename', {'attr': 'value'})
