from scheme import *
from tests.util import *

class TestSequence(FieldTestCase):
    def _generate_sequences(self):
        today, today_text = construct_today()
        yesterday, yesterday_text = construct_today(-1)
        tomorrow, tomorrow_text = construct_today(+1)

        return ([yesterday, today, tomorrow],
            [yesterday_text, today_text, tomorrow_text])

    def test_construction(self):
        with self.assertRaises(TypeError):
            Sequence(True)
        with self.assertRaises(TypeError):
            Sequence(Text(), min_length='bad')
        with self.assertRaises(TypeError):
            Sequence(Text(), min_length=-2)
        with self.assertRaises(TypeError):
            Sequence(Text(), max_length='bad')
        with self.assertRaises(TypeError):
            Sequence(Text(), max_length=-2)

    def test_processing(self):
        field = Sequence(Date())

        self.assert_processed(field, None, self._generate_sequences())
        self.assert_processed(field, [], ancestry=['test'])
        self.assert_not_processed(field, 'invalid', True)

        field = Sequence(Integer())

        self.assert_processed(field, [1, 2, 3], [1, None, 3])

        expected_error = ValidationError(structure=[1,  INVALID_ERROR, 3])

        self.assert_not_processed(field, expected_error, [1, '', 3])

    def test_preprocessing(self):
        def preprocess(value):
            return [v.lower() for v in value]

        field = Sequence(Text(), preprocessor=preprocess)

        self.assert_processed(field, None, [], ['one', 'two'])
        self.assertEqual(field.process(['One', 'Two']), ['one', 'two'])

    def test_null_values(self):
        field = Sequence(Integer(nonnull=True))

        self.assert_processed(field, [], [1, 2, 3])

        expected_error = ValidationError(structure=[1, NULL_ERROR, 3])

        self.assert_not_processed(field, expected_error, [1, None, 3])

    def test_min_length(self):
        field = Sequence(Date(), min_length=2)
        a, b = self._generate_sequences()

        self.assert_processed(field, (a, b), (a[:2], b[:2]))
        self.assert_not_processed(field, 'min_length', (a[:1], b[:1]))

    def test_max_length(self):
        field = Sequence(Date(), max_length=2)
        a, b = self._generate_sequences()

        self.assert_processed(field, (a[:1], b[:1]), (a[:2], b[:2]))
        self.assert_not_processed(field, 'max_length', (a, b))

    def test_unique_values(self):
        field = Sequence(Integer(), unique=True)

        self.assert_processed(field, [], [1], [1, 2])
        self.assert_not_processed(field, 'duplicate', [1, 1])

    def test_undefined_field(self):
        undefined = Undefined(Integer())
        field = Sequence(undefined)

        self.assert_processed(field, None, [], [1], [1, 2])

        undefined = Undefined()
        field = Sequence(undefined)

        with self.assertRaises(UndefinedFieldError):
            field.process([1, 2])
        with self.assertRaises(UndefinedFieldError):
            field.extract([1, 2])
        with self.assertRaises(UndefinedFieldError):
            field.instantiate([1, 2])
        with self.assertRaises(UndefinedFieldError):
            field.interpolate([1, 2], {})

        undefined.define(Integer())

        self.assert_processed(field, None, [], [1], [1, 2])

    def test_naive_extraction(self):
        field = Sequence(Integer())
        self.assertIs(field.extract(None), None)

        with self.assertRaises(FieldExcludedError):
            field.extract([], required=True)
        with self.assertRaises(CannotExtractError):
            field.extract({})

        value = [1, 2, 3]
        extracted = field.extract(value)

        self.assertIsNot(extracted, value)
        self.assertEqual(extracted, value)

    def test_naive_extraction_with_nesting(self):
        field = Sequence(Sequence(Integer()))
        value = [[1], [2], [3]]

        extracted = field.extract(value)

        self.assertIsNot(extracted, value)
        self.assertEqual(extracted, value)
        for i in (0, 1, 2):
            self.assertIsNot(extracted[1], value[1])

    def test_naive_extraction_with_nested_extractors(self):
        field = Sequence(Integer(extractor=valuewrapper.extract))
        value = [valuewrapper(None, 1), valuewrapper(None, 2)]
        extracted = field.extract(value)

        self.assertIsInstance(extracted, list)
        self.assertEqual(extracted, [1, 2])

    def test_mediated_extraction(self):
        field = Sequence(Integer(), extractor=listwrapper.extract)

        with self.assertRaises(CannotExtractError):
            field.extract({})

        value = listwrapper(None, [1, 2])
        extracted = field.extract(value)

        self.assertIsInstance(extracted, list)
        self.assertEqual(extracted, [1, 2])

    def test_mediated_extraction_with_nested_extractors(self):
        field = Sequence(Integer(extractor=valuewrapper.extract), extractor=listwrapper.extract)
        value = listwrapper(None, [valuewrapper(None, 1), valuewrapper(None, 2)])
        extracted = field.extract(value)

        self.assertIsInstance(extracted, list)
        self.assertEqual(extracted, [1, 2])

    def test_filter(self):
        field = Sequence(Structure({'one': Integer(one=True), 'two': Integer()}), one=False)

        self.assertIs(field.filter(), field)
        self.assertIsNone(field.filter(one=True))

        filtered = field.filter(one=False)

        self.assertIsInstance(filtered, Sequence)
        self.assertIsNot(filtered, field)
        self.assertEqual(set(filtered.item.structure.keys()), set(['two']))

        field = Sequence(Structure({'one': Integer()}, one=True))

        with self.assertRaises(CannotFilterError):
            field.filter(one=False)

    def test_mediated_instantiation(self):
        field = Sequence(Integer(), instantiator=listwrapper)

        self.assertIs(field.instantiate(None), None)

        instance = field.instantiate([1, 2])

        self.assertIsInstance(instance, listwrapper)
        self.assertEqual(instance.list, [1, 2])

        instance = field.instantiate([])

        self.assertIsInstance(instance, listwrapper)
        self.assertEqual(instance.list, [])

    def test_mediated_instantiation_with_nested_instantiators(self):
        field = Sequence(Integer(instantiator=valuewrapper), instantiator=listwrapper)
        instance = field.instantiate([1, 2])

        self.assertIsInstance(instance, listwrapper)
        self.assertIsInstance(instance.list[0], valuewrapper)
        self.assertEqual(instance.list[0].value, 1)
        self.assertIsInstance(instance.list[1], valuewrapper)
        self.assertEqual(instance.list[1].value, 2)

    def test_naive_instantiation_with_nested_instantiators(self):
        field = Sequence(Integer(instantiator=valuewrapper))
        instance = field.instantiate([1, 2])

        self.assertIsInstance(instance, list)
        self.assertIsInstance(instance[0], valuewrapper)
        self.assertEqual(instance[0].value, 1)
        self.assertIsInstance(instance[1], valuewrapper)
        self.assertEqual(instance[1].value, 2)

    def test_interpolation(self):
        field = Sequence(Integer())

        with self.assertRaises(CannotInterpolateError):
            field.interpolate({}, {})

        self.assert_interpolated(field, None, [])
        self.assert_interpolated(field, (['${alpha}', '${beta}'], [1, 2]), alpha=1, beta=2)
        self.assert_interpolated(field, ([1, 2], [1, 2]))
        self.assert_interpolated(field, ('${value}', [1, 2]), value=['${alpha}', '${beta}'],
            alpha=1, beta=2)

    def test_transformation(self):
        field = Sequence(Integer())
        transformed = field.transform(lambda _: False)

        self.assertIs(transformed, field)

        transformed = field.transform(lambda f: f)

        self.assertIs(transformed, field)

        def will_transform(f):
            if isinstance(f, Integer):
                return f.clone(description='transformed')

        transformed = field.transform(will_transform)

        self.assertIsNot(transformed, field)
        self.assertIsNot(transformed.item, field.item)
        self.assertEqual(transformed.item.description, 'transformed')

        def will_not_transform(f):
            if isinstance(f, Text):
                return f.clone(description='transformed')

        transformed = field.transform(will_not_transform)

        self.assertIs(transformed, field)
        self.assertIs(transformed.item, field.item)

    def test_description(self):
        field = Sequence(Integer())

        self.assertEqual(field.describe(), {'fieldtype': 'sequence', 'structural': True,
            'item': {'fieldtype': 'integer'}})

        field = Sequence(Integer(), default=[1, 2])

        self.assertEqual(field.describe(), {'fieldtype': 'sequence', 'structural': True,
            'item': {'fieldtype': 'integer'}, 'default': [1, 2]})

    def test_visit(self):
        def visit(f):
            return f['fieldtype']

        field = Sequence(Text())
        visited = Field.visit(field.describe(), visit)

        self.assertEqual(visited, {'item': 'text'})
