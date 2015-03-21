try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from scheme import *
from tests.util import *

class TestStructuralError(TestCase):
    def test_construction(self):
        error = StructuralError({'token': 'error'})
        self.assertEqual(error.errors, [{'token': 'error'}])

        error = StructuralError(token='error')
        self.assertEqual(error.errors, [{'token': 'error'}])

    def test_substantive(self):
        error = StructuralError()
        self.assertFalse(error.substantive)

        error = StructuralError(token='error')
        self.assertTrue(error.substantive)

    def test_append(self):
        error = StructuralError()
        suberror = {'item': StructuralError()}
        self.assertIs(error.attach(suberror), error)
        self.assertIs(error.structure, suberror)

    def test_capture(self):
        error = StructuralError()
        for i in range(1, 3):
            try:
                raise TypeError()
            except TypeError:
                error.capture()
            self.assertEqual(len(error.tracebacks), i)

    def test_merge(self):
        error = StructuralError({'token': 'error'})
        self.assertIs(error.merge(StructuralError({'token': 'error2'})), error)
        self.assertEqual(error.errors, [{'token': 'error'}, {'token': 'error2'}])

    def test_serialize(self):
        error = StructuralError({'token': 'error'}, 'simple-error')
        serialized = error.serialize()
        self.assertEqual(serialized, ([{'token': 'error'}, {'message': 'simple-error'}], None))
        self.assertIs(error.serialize(), serialized)
        
        reserialized = error.serialize(True)
        self.assertEqual(reserialized, ([{'token': 'error'}, {'message': 'simple-error'}], None))
        self.assertIsNot(reserialized, serialized)

        error = StructuralError(structure={
            'item': StructuralError({'token': 'error'}),
            'item2': StructuralError(structure={'item': StructuralError({'token': 'error'})}),
        })
        self.assertEqual(error.serialize(), (None, {
            'item': [{'token': 'error'}],
            'item2': {'item': [{'token': 'error'}]},
        }))

        error = StructuralError({'token': 'error'}, structure={'item': StructuralError({'token': 'error'})})
        self.assertEqual(error.serialize(), ([{'token': 'error'}], {'item': [{'token': 'error'}]}))

        error = StructuralError(structure=[
            StructuralError(structure={'item': StructuralError({'token': 'error'})}),
            [1, 2, 3],
            StructuralError({'token': 'error'}),
        ])
        self.assertEqual(error.serialize(), (None, [
            {'item': [{'token': 'error'}]},
            None,
            [{'token': 'error'}],
        ]))

    def test_unserialize(self):
        error = StructuralError.unserialize(([{'token': 'error'}], {'item': [{'token': 'error'}]}))
        self.assertIsInstance(error, StructuralError)
        self.assertEqual(error.errors, [{'token': 'error'}])


