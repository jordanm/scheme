from scheme import *
from tests.util import *

class TestMap(FieldTestCase):
    def test_construction(self):
        with self.assertRaises(TypeError):
            Map(True)
        with self.assertRaises(TypeError):
            Map(Text(), True)
        with self.assertRaises(TypeError):
            Map(Text(), required_keys=True)

        field = Map(Text(), required_keys='one two three')
        self.assertEqual(field.required_keys, ['one', 'two', 'three'])

    def test_processing(self):
        field = Map(Integer())
        self.assert_processed(field, None)
        self.assert_not_processed(field, 'invalidkeys', {1: 1})

        for valid in [{}, {'a': 1}, {'a': 1, 'b': 2}, {'a': None}]:
            self.assert_processed(field, (valid, valid))

        expected_error = ValidationError(structure={'a': INVALID_ERROR, 'b': 2})
        self.assert_not_processed(field, expected_error, {'a': '', 'b': 2})

    def test_preprocessing(self):
        def preprocess(value):
            return dict((k, v.lower()) for k, v in value.items())

        field = Map(Text(), preprocessor=preprocess)
        self.assert_processed(field, None, {}, {'a': 'one'}, {'a': 'one', 'b': 'two'})
        self.assertEqual(field.process({'a': 'TEST', 'b': 'test'}), {'a': 'test', 'b': 'test'})

    def test_null_values(self):
        field = Map(Integer(nonnull=True))
        self.assert_processed(field, {}, {'a': 1})

        expected_error = ValidationError(structure={'a': NULL_ERROR, 'b': 2})
        self.assert_not_processed(field, expected_error, {'a': None, 'b': 2})

    def test_required_keys(self):
        field = Map(Integer(), required_keys=('a',))
        self.assert_processed(field, {'a': 1})

        expected_error = ValidationError(structure={'a': REQUIRED_ERROR})
        self.assert_not_processed(field, expected_error, {})

    def test_explicit_key(self):
        field = Map(Integer(), key=Integer())
        self.assert_processed(field, {}, {1: 1}, {1: 1, 2: 2})
        self.assert_not_processed(field, 'invalidkeys', {'a': 1})

    def test_undefined_fields(self):
        undefined = Undefined(Integer())
        field = Map(undefined)
        self.assert_processed(field, None, {}, {'a': 1}, {'a': 1, 'b': 2})

        undefined = Undefined()
        field = Map(undefined)

        with self.assertRaises(UndefinedFieldError):
            field.process({'a': 1})
        with self.assertRaises(UndefinedFieldError):
            field.extract({'a': 1})
        with self.assertRaises(UndefinedFieldError):
            field.instantiate({'a': 1})
        with self.assertRaises(UndefinedFieldError):
            field.interpolate({'a': 1}, {})

        undefined.define(Integer())
        self.assert_processed(field, None, {}, {'a': 1}, {'a': 1, 'b': 2})

    def test_naive_extraction(self):
        field = Map(Integer())
        self.assertIs(field.extract(None), None)

        with self.assertRaises(FieldExcludedError):
            field.extract({}, required=True)

        value = {'a': 1, 'b': 2}
        extracted = field.extract(value)

        self.assertIsInstance(extracted, dict)
        self.assertIsNot(extracted, value)
        self.assertEqual(extracted, value)

    def test_naive_extraction_with_nesting(self):
        field = Map(Map(Integer()))
        value = {'a': {'a': 1}, 'b': {'b': 2}}
        extracted = field.extract(value)

        self.assertIsNot(extracted, value)
        self.assertIsNot(extracted['a'], value['a'])
        self.assertEqual(extracted, value)

    def test_mediated_extraction(self):
        field = Map(Integer(), extractor=attrmap.extract)
        with self.assertRaises(CannotExtractError):
            field.extract([])

        value = {'a': 1, 'b': 2}
        extracted = field.extract(attrmap(None, value))

        self.assertIsInstance(extracted, dict)
        self.assertIsNot(extracted, value)
        self.assertEqual(extracted, value)

    def test_mediated_extraction_with_nested_extractors(self):
        field = Map(Integer(extractor=valuewrapper.extract), extractor=attrmap.extract)
        value = attrmap(None, {'a': valuewrapper(None, 1), 'b': valuewrapper(None, 2)})
        extracted = field.extract(value)

        self.assertIsInstance(extracted, dict)
        self.assertEqual(extracted, {'a': 1, 'b': 2})

    def test_naive_extraction_with_nested_extractors(self):
        field = Map(Integer(extractor=valuewrapper.extract))
        value = {'a': valuewrapper(None, 1), 'b': valuewrapper(None, 2)}
        extracted = field.extract(value)

        self.assertIsInstance(extracted, dict)
        self.assertEqual(extracted, {'a': 1, 'b': 2})

    def test_filter(self):
        field = Map(Structure({'one': Integer(one=True), 'two': Integer()}), one=False)
        
        self.assertIs(field.filter(), field)
        self.assertIsNone(field.filter(one=True))

        filtered = field.filter(one=False)

        self.assertIsInstance(filtered, Map)
        self.assertIsNot(filtered, field)
        self.assertEqual(set(filtered.value.structure.keys()), set(['two']))

        field = Map(Structure({'one': Integer()}, one=True))

        with self.assertRaises(CannotFilterError):
            field.filter(one=False)

    def test_mediated_instantiation(self):
        field = Map(Integer(), instantiator=attrmap)
        self.assertIs(field.instantiate(None), None)

        instance = field.instantiate({'a': 1, 'b': 2})
        self.assertIsInstance(instance, attrmap)
        self.assertEqual(instance.a, 1)
        self.assertEqual(instance.b, 2)

        instance = field.instantiate({})
        self.assertIsInstance(instance, attrmap)

    def test_mediated_instantiation_with_nested_instantiators(self):
        field = Map(Integer(instantiator=valuewrapper), instantiator=attrmap)
        instance = field.instantiate({'a': 1, 'b': 2})

        self.assertIsInstance(instance, attrmap)
        self.assertIsInstance(instance.a, valuewrapper)
        self.assertEqual(instance.a.value, 1)

    def test_interpolation(self):
        field = Map(Integer())
        with self.assertRaises(CannotInterpolateError):
            field.interpolate([], {})

        self.assert_interpolated(field, None, {}, ({'alpha': 1, 'beta': 2},
            {'alpha': 1, 'beta': 2}))
        self.assert_interpolated(field, ({'alpha': '${alpha}', 'beta': '${beta}'},
            {'alpha': 1, 'beta': 2}), alpha=1, beta=2)
        self.assert_interpolated(field, ({'alpha': '${alpha}', 'beta': '${beta}'},
            {'alpha': 1}), alpha=1)
        self.assert_interpolated(field, ('${value}', {'alpha': 1, 'beta': 2}),
            value={'alpha': '${alpha}', 'beta': '${beta}'}, alpha=1, beta=2)

    def test_transformation(self):
        field = Map(Integer())

        transformed = field.transform(lambda _: False)
        self.assertIs(transformed, field)

        transformed = field.transform(lambda f: f)
        self.assertIs(transformed, field)

        def will_transform(f):
            if isinstance(f, Integer):
                return f.clone(description='transformed')

        transformed = field.transform(will_transform)
        self.assertIsNot(transformed, field)
        self.assertIsNot(transformed.value, field.value)
        self.assertEqual(transformed.value.description, 'transformed')

        def will_not_transform(f):
            if isinstance(f,Text):
                return f.clone(description='transformed')

        transformed = field.transform(will_not_transform)
        self.assertIs(transformed, field)

    def test_description(self):
        field = Map(Text())
        self.assertEqual(field.describe(), {'fieldtype': 'map', 'structural': True,
            'value': {'fieldtype': 'text'}})

        field = Map(Text(), Integer())
        self.assertEqual(field.describe(), {'fieldtype': 'map', 'structural': True,
            'value': {'fieldtype': 'text'}, 'key': {'fieldtype': 'integer'}})

        field = Map(Text(), default={'alpha': 'one'})
        self.assertEqual(field.describe(), {'fieldtype': 'map', 'structural': True,
            'value': {'fieldtype': 'text'}, 'default': {'alpha': 'one'}})

    def test_visit(self):
        def visit(f):
            return f['fieldtype']

        field = Map(Text())
        visited = Field.visit(field.describe(), visit)
        self.assertEqual(visited, {'value': 'text'})

        field = Map(Text(), Integer())
        visited = Field.visit(field.describe(), visit)
        self.assertEqual(visited, {'value': 'text', 'key': 'integer'})
