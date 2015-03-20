from scheme import *
from tests.util import *

class TestUnion(FieldTestCase):
    def test_invalid_instantiation(self):
        with self.assertRaises(TypeError):
            Union()

        with self.assertRaises(TypeError):
            Union(True)

    def test_processing(self):
        field = Union((Text(), Integer()))
        self.assert_processed(field, None, 'testing', 1, ancestry=['test'])
        self.assert_not_processed(field, 'invalid', True, {}, [])

        field = Union((Map(Integer()), Text()))
        self.assert_processed(field, None, {'a': 1}, 'testing')
        self.assert_not_processed(field, 'invalid', 1, True, [])

    def test_undefined_fields(self):
        undefined = Undefined(Integer())
        field = Union((Text(), undefined, Boolean()))
        self.assert_processed(field, None, 'testing', 1, True)
        self.assert_not_processed(field, 'invalid', {}, [])

        undefined = Undefined()
        field = Union((Text(), undefined, Boolean()))

        with self.assertRaises(UndefinedFieldError):
            field.process(2)
        with self.assertRaises(UndefinedFieldError):
            field.process([])
        #self.assertRaises(UndefinedFieldError, lambda: field.extract(True))

        undefined.define(Integer())
        self.assert_processed(field, None, 'testing', 1, True)
        self.assert_not_processed(field, 'invalid', {}, [])

    def test_naive_extraction(self):
        field = Union((Map(Text()), Integer(), Sequence(Boolean())))
        self.assertIs(field.extract(None), None)

        with self.assertRaises(FieldExcludedError):
            field.extract({}, required=True)

        for value in ({'a': 'a'}, 2, [True, False]):
            extracted = field.extract(value)
            self.assertIsInstance(extracted, type(value))
            self.assertEqual(extracted, value)

    def test_transformation(self):
        field = Union((Text(), Integer()))

        transformed = field.transform(lambda _: False)
        self.assertIs(transformed, field)

        transformed = field.transform(lambda f: f)
        self.assertIs(transformed, field)

        def will_transform(f):
            if isinstance(f, Integer):
                return f.clone(description='transformed')

        transformed = field.transform(will_transform)
        self.assertIsNot(transformed, field)
        self.assertIsNot(transformed.fields[1], field.fields[1])
        self.assertEqual(transformed.fields[1].description, 'transformed')

        def will_not_transform(f):
            if isinstance(f, Boolean):
                return f.clone(description='transformed')

        transformed = field.transform(will_not_transform)
        self.assertIs(transformed, field)

    def test_description(self):
        field = Union((Text(), Integer()))
        self.assertEqual(field.describe(), {'fieldtype': 'union', 'structural': True,
            'fields': [{'fieldtype': 'text'}, {'fieldtype': 'integer'}]})

    def test_visit(self):
        def visit(f):
            return f['fieldtype']

        field = Union((Text(), Integer()))
        self.assertEqual(Field.visit(field.describe(), visit), 
            {'fields': ('text', 'integer')})
