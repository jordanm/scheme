from scheme import *
from scheme.util import string
from tests.util import *

class TestTuple(FieldTestCase):
    def test_invalid_instantiation(self):
        for invalid_value in (True, [], [True]):
            with self.assertRaises(TypeError):
                Tuple(invalid_value)

    def test_processing(self):
        field = Tuple((Text(), Boolean(), Integer()))
        self.assert_processed(field, None)
        self.assert_not_processed(field, 'invalid', True)

        for valid in [('test', True, 1), ('test', None, 1)]:
            self.assert_processed(field, (valid, valid), ancestry=['test'])

        self.assert_not_processed(field, 'length', ((), ()))

        expected_error = ValidationError(structure=['test', INVALID_ERROR, 1])
        self.assert_not_processed(field, expected_error,
            (('test', 'a', 1), ('test', 'a', 1)))

    def test_preprocessing(self):
        def preprocess(value):
            processed = []
            for v in value:
                if isinstance(v, string):
                    v = v.lower()
                processed.append(v)
            return tuple(processed)

        field = Tuple((Integer(), Text(), Text()), preprocessor=preprocess)
        self.assert_processed(field, None)
        self.assertEqual(field.process((1, 'one', 'two')), (1, 'one', 'two'))
        self.assertEqual(field.process((1, 'ONE', 'two')), (1, 'one', 'two'))

    def test_null_values(self):
        field = Tuple((Text(nonnull=True), Integer()))
        for valid in [('test', 1), ('test', None)]:
            self.assert_processed(field, (valid, valid))

        expected_error = ValidationError(structure=[NULL_ERROR, None])
        self.assert_not_processed(field, expected_error,
            ((None, None), (None, None)))

    def test_undefined_field(self):
        undefined = Undefined(Integer())
        field = Tuple((Text(), undefined, Text()))
        self.assert_processed(field, None, (('', 1, ''), ('', 1, '')))

        undefined = Undefined()
        field = Tuple((Text(), undefined, Text()))
        with self.assertRaises(UndefinedFieldError):
            field.process(('', 1, ''))
        with self.assertRaises(UndefinedFieldError):
            field.extract(('', 1, ''))
        with self.assertRaises(UndefinedFieldError):
            field.instantiate(('', 1, ''))
        with self.assertRaises(UndefinedFieldError):
            field.interpolate(('', 1, ''), {})

        undefined.define(Integer())
        self.assert_processed(field, None, (('', 1, ''), ('', 1, '')))

    def test_naive_extraction(self):
        field = Tuple((Integer(), Text()))
        self.assertIs(field.extract(None), None)

        with self.assertRaises(FieldExcludedError):
            field.extract((), required=True)
        with self.assertRaises(CannotExtractError):
            field.extract({})

        value = (1, 'test')
        extracted = field.extract(value)

        self.assertIsNot(value, extracted)
        self.assertEqual(value, extracted)

    def test_naive_extraction_with_nesting(self):
        field = Tuple((Tuple((Integer(),)), Text()))
        value = ((1,), 'test')

        extracted = field.extract(value)
        self.assertIsNot(value, extracted)
        self.assertIsNot(value[0], extracted[0])
        self.assertEqual(value, extracted)

    def test_mediated_extraction(self):
        field = Tuple((Integer(), Text()), extractor=listwrapper.extract)
        with self.assertRaises(CannotExtractError):
            field.extract({})

        value = listwrapper(None, (1, 'test'))
        extracted = field.extract(value)

        self.assertIsInstance(extracted, tuple)
        self.assertEqual(extracted, (1, 'test'))

    def test_mediated_extraction_with_nested_extractors(self):
        field = Tuple((Integer(extractor=valuewrapper.extract), Text()), extractor=listwrapper.extract)
        value = listwrapper(None, (valuewrapper(None, 1), 'test'))
        extracted = field.extract(value)

        self.assertIsInstance(extracted, tuple)
        self.assertEqual(extracted, (1, 'test'))

    def test_naive_extraction_with_nested_extractors(self):
        field = Tuple((Integer(), Text(extractor=valuewrapper.extract)))
        value = (1, valuewrapper(None, 'test'))
        extracted = field.extract(value)

        self.assertIsInstance(extracted, tuple)
        self.assertEqual(extracted, (1, 'test'))

    def test_filter(self):
        field = Tuple((Integer(), Structure({'one': Integer(one=True), 'two': Integer()})), one=False)

        self.assertIs(field.filter(), field)
        self.assertIsNone(field.filter(one=True))

        filtered = field.filter(one=False)

        self.assertIsInstance(filtered, Tuple)
        self.assertIsNot(filtered, field)
        self.assertEqual(set(filtered.values[1].structure.keys()), set(['two']))

        field = Tuple((Integer(), Text(one=True)))

        with self.assertRaises(CannotFilterError):
            field.filter(one=False)

    def test_mediated_instantiation(self):
        field = Tuple((Integer(), Text()), instantiator=listwrapper)
        self.assertIs(field.instantiate(None), None)
        instance = field.instantiate((1, 'test'))

        self.assertIsInstance(instance, listwrapper)
        self.assertEqual(instance.list, (1, 'test'))

    def test_mediated_instantiation_with_nested_instantiators(self):
        field = Tuple((Integer(instantiator=valuewrapper), Text()), instantiator=listwrapper)
        instance = field.instantiate((1, 'test'))

        self.assertIsInstance(instance, listwrapper)
        self.assertIsInstance(instance.list[0], valuewrapper)
        self.assertEqual(instance.list[0].value, 1)
        self.assertEqual(instance.list[1], 'test')

    def test_naive_instantiation_with_nested_instantiators(self):
        field = Tuple((Integer(), Text(instantiator=valuewrapper)))
        instance = field.instantiate((1, 'test'))

        self.assertIsInstance(instance, tuple)
        self.assertEqual(instance[0], 1)
        self.assertIsInstance(instance[1], valuewrapper)
        self.assertEqual(instance[1].value, 'test')

    def test_interpolation(self):
        field = Tuple((Integer(), Text()))
        with self.assertRaises(CannotInterpolateError):
            field.interpolate({}, {})

        self.assert_interpolated(field, None, ((1, 'two'), (1, 'two')))
        self.assert_interpolated(field, (('${alpha}', '${beta}'), (1, 'two')),
            alpha=1, beta='two')
        self.assert_interpolated(field, ('${value}', (1, 'two')),
            value=('${alpha}', '${beta}'), alpha=1, beta='two')

    def test_transformation(self):
        field = Tuple((Integer(), Text()))

        transformed = field.transform(lambda _: False)
        self.assertIs(transformed, field)

        transformed = field.transform(lambda f: f)
        self.assertIs(transformed, field)

        def will_transform(f):
            if isinstance(f, Integer):
                return f.clone(description='transformed')

        transformed = field.transform(will_transform)
        self.assertIsNot(transformed, field)
        self.assertIsNot(transformed.values[0], field.values[0])
        self.assertIs(transformed.values[1], field.values[1])
        self.assertEqual(transformed.values[0].description, 'transformed')
        self.assertNotEqual(transformed.values[1].description, 'transformed')

        def will_not_transform(f):
            if isinstance(f, Boolean):
                return f.clone(description='transformed')

        transformed = field.transform(will_not_transform)
        self.assertIs(transformed, field)

    def test_description(self):
        field = Tuple((Text(), Integer()))
        self.assertEqual(field.describe(), {'fieldtype': 'tuple', 'structural': True,
            'values': [{'fieldtype': 'text'}, {'fieldtype': 'integer'}]})

        field = Tuple((Text(), Integer()), default=('test', 1))
        self.assertEqual(field.describe(), {'fieldtype': 'tuple', 'structural': True,
            'values': [{'fieldtype': 'text'}, {'fieldtype': 'integer'}],
            'default': ('test', 1)})

    def test_visit(self):
        def visit(f):
            return f['fieldtype']

        field = Tuple((Text(), Integer()))
        visited = Field.visit(field.describe(), visit)
        self.assertEqual(visited, {'values': ('text', 'integer')})
