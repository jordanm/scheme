from scheme import *
from tests.util import *

class TestStructure(FieldTestCase):
    maxDiff=None
    class ExtractionTarget(object):
        def __init__(self, **params):
            self.__dict__.update(**params)

    def test_instantiation(self):
        field = Structure({}, key_order='one two')
        self.assertEqual(field.key_order, ['one', 'two'])

        field = Structure({'a': Integer(default=1), 'b': Boolean()}, generate_default=True)
        self.assertEqual(field.default, {'a': 1})

    def test_invalid_instantiation(self):
        with self.assertRaises(TypeError):
            Structure(True)
        with self.assertRaises(TypeError):
            Structure({'a': True})
        with self.assertRaises(TypeError):
            Structure({}, polymorphic_on=True)
        with self.assertRaises(TypeError):
            Structure({}, key_order=True)
        with self.assertRaises(TypeError):
            Structure({'a': True}, polymorphic_on='type')
        with self.assertRaises(ValueError):
            Structure({}, generate_default='test')

    def test_processing(self):
        field = Structure({})
        self.assert_processed(field, None, {})
        self.assert_processed(field, {}, ancestry=['test'])
        self.assert_not_processed(field, 'invalid', True)

        field = Structure({'a': Integer(), 'b': Text(), 'c': Boolean()})
        self.assert_processed(field, None, {}, {'a': None}, {'a': 1},
            {'a': 1, 'b': None}, {'a': 1, 'b': 'b', 'c': True})

        expected_error = ValidationError(structure={'a': INVALID_ERROR, 'b': 'b', 'c': True})
        self.assert_not_processed(field, expected_error, {'a': '', 'b': 'b', 'c': True})

    def test_preprocessing(self):
        def preprocess(value):
            if 'a' in value:
                value = value.copy()
                value['a'] = value['a'].lower()
            return value

        field = Structure({'a': Text(), 'b': Integer()}, preprocessor=preprocess)
        self.assert_processed(field, None, {}, {'a': 'test'}, {'b': 2}, {'a': 'test', 'b': 2})
        self.assertEqual(field.process({'a': 'TEST', 'b': 2}), {'a': 'test', 'b': 2})

    def test_processing_with_key_order(self):
        field = Structure({'alpha': Text(), 'beta': Text(), 'gamma': Text()}, key_order='gamma alpha beta')
        self.assert_processed(field, None, {})
        self.assert_not_processed(field, 'invalid', True)

    def test_required_values(self):
        field = Structure({'a': Integer(required=True), 'b': Text()})
        self.assert_processed(field, {'a': None}, {'a': 1}, {'a': 1, 'b': 'b'})

        expected_error = ValidationError(structure={'a': REQUIRED_ERROR, 'b': 'b'})
        self.assert_not_processed(field, expected_error, {'b': 'b'})

    def test_ignore_null_values(self):
        field = Structure({'a': Integer()})
        self.assertEqual(field.process({'a': None}, INBOUND), {'a': None})

        field = Structure({'a': Integer(ignore_null=True)})
        self.assertEqual(field.process({'a': None}, INBOUND), {})

    def test_unknown_values(self):
        field = Structure({'a': Integer()})
        self.assert_processed(field, {}, {'a': 1})

        expected_error = ValidationError(structure={'a': 1, 'z': UNKNOWN_ERROR})
        self.assert_not_processed(field, expected_error, {'a': 1, 'z': True})

        field = Structure({'a': Integer()}, strict=False)
        self.assert_processed(field, {}, {'a': 1})
        self.assertEqual(field.process({'a': 1, 'z': True}, INBOUND), {'a': 1})

    def test_default_values(self):
        field = Structure({'a': Integer(default=2)})
        self.assertEqual(field.process({'a': 1}, INBOUND), {'a': 1})
        self.assertEqual(field.process({}, INBOUND), {'a': 2})
        self.assertEqual(field.process({'a': 1}, OUTBOUND), {'a': 1})
        self.assertEqual(field.process({}, OUTBOUND), {})

    def test_polymorphism(self):
        field = Structure({
            'alpha': {'a': Integer()},
            'beta': {'b': Integer()},
        }, polymorphic_on=Text(name='id'))

        self.assert_processed(field, None)
        self.assert_not_processed(field, 'required', {})

        self.assert_processed(field, {'id': 'alpha', 'a': 1}, {'id': 'beta', 'b': 2})
        self.assert_not_processed(field, 'unrecognized', {'id': 'gamma', 'g': 3})

        expected_error = ValidationError(structure={'id': 'alpha', 'b': UNKNOWN_ERROR})
        self.assert_not_processed(field, expected_error, {'id': 'alpha', 'b': 2})

        field = Structure({
            'alpha': {'a': Integer(default=1)},
            'beta': {'b': Integer(default=2)},
        }, polymorphic_on='type', generate_default='alpha')

        self.assertEqual(field.default, {'type': 'alpha', 'a': 1})

        with self.assertRaises(ValueError):
            Structure({'alpha': {}}, polymorphic_on='type', generate_default=True)

    def test_polymorphism_with_field_autogeneration(self):
        field = Structure({
            'alpha': {'a': Integer()},
            'beta': {'b': Integer()},
        }, polymorphic_on='id')

        self.assert_processed(field, None)
        self.assert_not_processed(field, 'required', {})

        self.assert_processed(field, {'id': 'alpha', 'a': 1}, {'id': 'beta', 'b': 2})
        self.assert_not_processed(field, 'invalid', {'id': 'gamma', 'g': 3})

        expected_error = ValidationError(structure={'id': 'alpha', 'b': UNKNOWN_ERROR})
        self.assert_not_processed(field, expected_error, {'id': 'alpha', 'b': 2})

    def test_polymorphism_with_common_fields(self):
        field = Structure({
            '*': {'n': Integer()},
            'alpha': {'a': Integer()},
            'beta': {'b': Integer()},
        }, polymorphic_on='id')

        self.assert_processed(field, None)
        self.assert_processed(field, {'id': 'alpha', 'a': 1, 'n': 3},
            {'id': 'beta', 'b': 2, 'n': 3})

    def test_undefined_fields(self):
        undefined = Undefined(Integer())
        field = Structure({'a': undefined})
        self.assert_processed(field, None, {}, {'a': 1})

        undefined = Undefined()
        field = Structure({'a': undefined})
        with self.assertRaises(UndefinedFieldError):
            field.process({'a': 1})
        with self.assertRaises(UndefinedFieldError):
            field.extract({'a': 1})
        with self.assertRaises(UndefinedFieldError):
            field.instantiate({'a': 1})
        with self.assertRaises(UndefinedFieldError):
            field.interpolate({'a': 1}, {})

        undefined.define(Integer())
        self.assert_processed(field, None, {}, {'a': 1})

    def test_undefined_polymorphic_fields(self):
        undefined = Undefined(Integer())
        field = Structure({'a': {'a': undefined}}, polymorphic_on='type')
        self.assert_processed(field, None, {'type': 'a', 'a': 1})

        undefined = Undefined()
        field = Structure({'a': {'a': undefined}}, polymorphic_on='type')
        with self.assertRaises(UndefinedFieldError):
            field.process({'type': 'a', 'a': 1})
        with self.assertRaises(UndefinedFieldError):
            field.extract({'type': 'a', 'a': 1})
        with self.assertRaises(UndefinedFieldError):
            field.instantiate({'type': 'a', 'a': 1})
        with self.assertRaises(UndefinedFieldError):
            field.interpolate({'type': 'a', 'a': 1}, {})

        undefined.define(Integer())
        self.assert_processed(field, None, {'type': 'a', 'a': 1})

    def test_naive_extraction(self):
        field = Structure({'a': Integer()})
        self.assertIs(field.extract(None), None)

        with self.assertRaises(FieldExcludedError):
            field.extract({}, required=True)
        with self.assertRaises(CannotExtractError):
            field.extract([])

        value = {'a': 1}
        extracted = field.extract(value)

        self.assertIsNot(extracted, value)
        self.assertEqual(extracted, value)

        extracted = field.extract({'a': 1, 'b': 2})
        self.assertEqual(extracted, value)

        extracted = field.extract({})
        self.assertEqual(extracted, {})

        extracted = field.extract({'a': None})
        self.assertEqual(extracted, {})

    def test_naive_extraction_with_nesting(self):
        field = Structure({'a': Structure({'a': Integer()})})
        value = {'a': {'a': 1}}

        extracted = field.extract(value)
        self.assertIsNot(extracted, value)
        self.assertIsNot(extracted['a'], value['a'])
        self.assertEqual(extracted, value)

    def test_naive_extraction_with_polymorphism(self):
        field = Structure({
            'alpha': {'a': Integer()},
            'beta': {'b': Integer()},
        }, polymorphic_on=Text(name='identity'))

        for value in ({'identity': 'alpha', 'a': 1}, {'identity': 'beta', 'b': 2}):
            extracted = field.extract(value)
            self.assertIsNot(extracted, value)
            self.assertEqual(extracted, value)

    def test_naive_extraction_with_nested_extractors(self):
        field = Structure({'a': Integer(), 'b': Text(extractor=valuewrapper.extract)})
        with self.assertRaises(CannotExtractError):
            field.extract([])

        value = {'a': 1, 'b': valuewrapper(None, 'test')}
        extracted = field.extract(value)

        self.assertIsInstance(extracted, dict)
        self.assertEqual(extracted, {'a': 1, 'b': 'test'})

    def test_mediated_extraction(self):
        field = Structure({'a': Integer(), 'b': Text()}, extractor=attrmap.extract)
        with self.assertRaises(CannotExtractError):
            field.extract([])

        value = attrmap(None, {'a': 1, 'b': 'test'})
        extracted = field.extract(value)

        self.assertIsInstance(extracted, dict)
        self.assertEqual(extracted, {'a': 1, 'b': 'test'})

    def test_mediated_extraction_with_nested_extractors(self):
        field = Structure({'a': Integer(extractor=valuewrapper.extract), 'b': Text()}, extractor=attrmap.extract)
        with self.assertRaises(CannotExtractError):
            field.extract([])

        value = attrmap(None, {'a': valuewrapper(None, 1), 'b': 'test'})
        extracted = field.extract(value)

        self.assertIsInstance(extracted, dict)
        self.assertEqual(extracted, {'a': 1, 'b': 'test'})

    def test_extraction_from_object(self):
        field = Structure({'a': Integer(), 'b': Text()})
        target = self.ExtractionTarget(a=1, b='b', c='c', d=4)
        extracted = field.extract(target, strict=False)

        self.assertIsInstance(extracted, dict)
        self.assertEqual(extracted, {'a': 1, 'b': 'b'})

        target = self.ExtractionTarget(a=1, c='c')
        extracted = field.extract(target, strict=False)

        self.assertIsInstance(extracted, dict)
        self.assertEqual(extracted, {'a': 1})

    def test_filter(self):
        field = Structure({'a': Integer(), 'b': Text(one=True)}, one=False)

        self.assertIs(field.filter(), field)
        self.assertIsNone(field.filter(one=True))
        
        filtered = field.filter(one=False)

        self.assertIsInstance(filtered, Structure)
        self.assertIsNot(filtered, field)
        self.assertEqual(set(filtered.structure.keys()), set(['a']))

        field = Structure({
            'alpha': {'a': Integer(), 'b': Text(one=True)},
            'beta': {'c': Integer(), 'd': Text(one=True)},
        }, polymorphic_on='type', one=False)

        self.assertIs(field.filter(), field)
        self.assertIsNone(field.filter(one=True))

        filtered = field.filter(one=False)

        self.assertIsInstance(filtered, Structure)
        self.assertIsNot(filtered, field)
        self.assertEqual(set(filtered.structure['alpha'].keys()), set(['a', 'type']))
        self.assertEqual(set(filtered.structure['beta'].keys()), set(['c', 'type']))

        field = Structure({'a': Structure({'b': Integer(one=True), 'c': Integer()})})
        filtered = field.filter(one=False)

        self.assertIsInstance(filtered, Structure)
        self.assertIsNot(filtered, field)
        self.assertIsInstance(filtered.structure['a'], Structure)
        self.assertEqual(set(filtered.structure['a'].structure.keys()), set(['c']))

    def test_mediated_instantiation(self):
        field = Structure({'a': Integer(), 'b': Text()}, instantiator=attrmap)
        self.assertIs(field.instantiate(None), None)

        instance = field.instantiate({'a': 1, 'b': 'test'})
        self.assertIsInstance(instance, attrmap)
        self.assertEqual(instance.a, 1)
        self.assertEqual(instance.b, 'test')

        instance = field.instantiate({})
        self.assertIsInstance(instance, attrmap)

    def test_mediated_instantiation_with_nested_instantiators(self):
        field = Structure({'a': Integer(instantiator=valuewrapper), 'b': Text()}, instantiator=attrmap)
        instance = field.instantiate({'a': 1, 'b': 'test'})

        self.assertIsInstance(instance, attrmap)
        self.assertIsInstance(instance.a, valuewrapper)
        self.assertEqual(instance.a.value, 1)
        self.assertEqual(instance.b, 'test')

    def test_naive_instantiation_with_nested_instantiators(self):
        field = Structure({'a': Integer(), 'b': Text(instantiator=valuewrapper)})
        instance = field.instantiate({'a': 1, 'b': 'test'})

        self.assertIsInstance(instance, dict)
        self.assertIsInstance(instance['b'], valuewrapper)
        self.assertEqual(instance['a'], 1)
        self.assertEqual(instance['b'].value, 'test')

    def test_mediated_instantiation_with_polymorphism(self):
        field = Structure({
            'alpha': {'a': Integer()},
            'beta': {'b': Integer()},
        }, polymorphic_on=Text(name='identity'), instantiator=attrmap)

        for value in ({'identity': 'alpha', 'a': 1}, {'identity': 'beta', 'b': 2}):
            instance = field.instantiate(value)
            self.assertIsInstance(instance, attrmap)
            self.assertEqual(instance.identity, value['identity'])

    def test_interpolation(self):
        field = Structure({'alpha': Integer(), 'beta': Text()})
        with self.assertRaises(CannotInterpolateError):
            field.interpolate([], {})

        self.assert_interpolated(field, None, {}, ({'alpha': 1, 'beta': 'two'},
            {'alpha': 1, 'beta': 'two'}))
        self.assert_interpolated(field, ({'alpha': '${alpha}', 'beta': '${beta}'},
            {'alpha': 1, 'beta': 'two'}), alpha=1, beta='two')
        self.assert_interpolated(field, ('${value}', {'alpha': 1, 'beta': 'two'}),
            value={'alpha': '${alpha}', 'beta': '${beta}'}, alpha=1, beta='two')

    def test_default_generation(self):
        field = Structure({'a': Integer(default=1), 'b': Text(default='test'), 'c': Boolean()})
        self.assertEqual(field.generate_defaults(), {'a': 1, 'b': 'test'})
        self.assertEqual(field.generate_defaults(sparse=False), {'a': 1, 'b': 'test', 'c': None})

        with self.assertRaises(ValueError):
            field.generate_defaults('test')

        field = Structure({'alpha': {'a': Integer(default=1)}, 'beta': {'b': Text(default='test')}},
            polymorphic_on='type')
        self.assertEqual(field.generate_defaults('alpha'), {'type': 'alpha', 'a': 1})
        self.assertEqual(field.generate_defaults(), {'alpha': {'type': 'alpha', 'a': 1},
            'beta': {'type': 'beta', 'b': 'test'}})

        with self.assertRaises(ValueError):
            field.generate_defaults('gamma')

    def test_structure_extension(self):
        field = Structure({'a': Integer()})
        with self.assertRaises(TypeError):
            field.extend({'b': True})

        clone = field.extend({'b': Text()})
        self.assertIsNot(clone, field)
        self.assertEqual(set(field.structure.keys()), set(['a']))
        self.assertEqual(set(clone.structure.keys()), set(['a', 'b']))

        clone = field.extend({'b': Text(name='b')})
        self.assertIsNot(clone, field)
        self.assertEqual(set(field.structure.keys()), set(['a']))
        self.assertEqual(set(clone.structure.keys()), set(['a', 'b']))

    def test_field_insertion(self):
        field = Structure({'a': Integer()})
        self.assertEqual(set(field.structure.keys()), set(['a']))

        field.insert(Text(name='b'))
        self.assertEqual(set(field.structure.keys()), set(['a', 'b']))

        field.insert(Boolean(name='a'), overwrite=False)
        self.assertIsInstance(field.structure['a'], Integer)

        field.insert(Boolean(name='a'), overwrite=True)
        self.assertIsInstance(field.structure['a'], Boolean)

        with self.assertRaises(TypeError):
            field.insert(True)
        with self.assertRaises(ValueError):
            field.insert(Text())

    def test_structure_merging(self):
        field = Structure({'a': Integer()})
        self.assertEqual(set(field.structure.keys()), set(['a']))

        replacement = Text(name='b')
        field.merge({'b': replacement})
        self.assertEqual(set(field.structure.keys()), set(['a', 'b']))
        self.assertIs(field.structure['b'], replacement)

        field.merge({'a': Boolean()}, prefer=False)
        self.assertIsInstance(field.structure['a'], Integer)

        field.merge({'a': Boolean()}, prefer=True)
        self.assertIsInstance(field.structure['a'], Boolean)

        replacement = Text(name='z')
        field.merge({'b': replacement})
        self.assertEqual(set(field.structure.keys()), set(['a', 'b']))
        self.assertIsInstance(field.structure['b'], Text)
        self.assertEqual(field.structure['b'].name, 'b')
        self.assertIsNot(field.structure['b'], replacement)

        with self.assertRaises(TypeError):
            field.merge({'b': True})

    def test_remove(self):
        field = Structure({'a': Integer(), 'b': Integer(), 'c': Integer()})

        field.remove('a')
        self.assertEqual(set(field.structure.keys()), set(['b', 'c']))

        field.remove('a')
        self.assertEqual(set(field.structure.keys()), set(['b', 'c']))

    def test_structure_replacement(self):
        field = Structure({'a': Integer(), 'b': Integer(), 'c': Integer()})

        replaced = field.replace({'d': Integer()})
        self.assertIs(replaced, field)

        replaced = field.replace({'a': Text(), 'b': Text(name='b'), 'd': Text()})
        self.assertIsNot(replaced, field)
        self.assertIsInstance(replaced.structure['a'], Text)
        self.assertIsInstance(replaced.structure['b'], Text)
        self.assertIsInstance(replaced.structure['c'], Integer)
        self.assertEqual(replaced.structure['a'].name, 'a')
        self.assertEqual(set(replaced.structure.keys()), set(['a', 'b', 'c']))

        with self.assertRaises(TypeError):
            field.replace({'a': True})

    def test_transformation(self):
        field = Structure({'a': Integer()})
        
        transformed = field.transform(lambda _: False)
        self.assertIs(transformed, field)

        transformed = field.transform(lambda f: f)
        self.assertIs(transformed, field)

        def will_transform(f):
            if isinstance(f, Integer):
                return f.clone(description='transformed')

        transformed = field.transform(will_transform)
        self.assertIsNot(transformed, field)
        self.assertIsNot(transformed.structure['a'], field.structure['a'])
        self.assertEqual(transformed.structure['a'].description, 'transformed')

        def will_not_transform(f):
            if isinstance(f, Text):
                return f.clone(description='transformed')

        transformed = field.transform(will_not_transform)
        self.assertIs(transformed, field)

    def test_partial_processing(self):
        field = Structure({'a': Integer(required=True, nonnull=True),
            'b': Text(required=True)})

        self.assertEqual(field.process({'a': 2}, INBOUND, partial=True), {'a': 2})

    def test_has_required_fields(self):
        field = Structure({'alpha': Text(required=True), 'beta': Integer()})
        self.assertTrue(field.has_required_fields)

        field = Structure({'alpha': Text(), 'beta': Integer()})
        self.assertFalse(field.has_required_fields)

        field = Structure({'alpha': {'alpha': Text()}}, polymorphic_on='type')
        self.assertTrue(field.has_required_fields)

    def test_get_field(self):
        field = Structure({'alpha': Text()})
        self.assertIs(field.get('alpha'), field.structure['alpha'])
        self.assertIs(field.get('beta'), None)

    def test_description(self):
        field = Structure({'alpha': Text()}, default={'alpha': 'alpha'})
        self.assertEqual(field.describe(), {'fieldtype': 'structure', 'structural': True,
            'structure': {'alpha': {'fieldtype': 'text', 'name': 'alpha'}},
            'default': {'alpha': 'alpha'}})

        field = Structure({'alpha': {'one': Integer()}, 'beta': {'one': Text()}}, polymorphic_on='type',
            default={'type': 'alpha', 'one': 1})
        self.assertEqual(field.describe(), {'fieldtype': 'structure', 'structural': True,
            'structure': {
                'alpha': {
                    'one': {'fieldtype': 'integer', 'name': 'one'},
                    'type': {'fieldtype': 'enumeration', 'name': 'type', 'constant': 'alpha',
                        'required': True, 'nonnull': True, 'enumeration': ['alpha', 'beta'],
                        'representation': "'alpha', 'beta'"},
                },
                'beta': {
                    'one': {'fieldtype': 'text', 'name': 'one'},
                    'type': {'fieldtype': 'enumeration', 'name': 'type', 'constant': 'beta',
                        'required': True, 'nonnull': True, 'enumeration': ['alpha', 'beta'],
                        'representation': "'alpha', 'beta'"},
                },
            },
            'polymorphic_on': {'fieldtype': 'enumeration', 'enumeration': ['alpha', 'beta'],
                'nonnull': True, 'required': True, 'name': 'type'},
            'default': {'type': 'alpha', 'one': 1},
        })

    def test_visit(self):
        def visit(f):
            return (f['fieldtype'], f['name'])

        field = Structure({'a': Text(), 'b': Integer()})
        visited = Field.visit(field.describe(), visit)

        self.assertEqual(visited, {'structure': {'a': ('text', 'a'), 'b': ('integer', 'b')}})

        field = Structure({'alpha': {'a': Text()}, 'beta': {'b': Integer()}}, polymorphic_on='t')
        visited = Field.visit(field.describe(), visit)

        self.assertEqual(visited, {'structure': {
            'alpha': {'a': ('text', 'a'), 't': ('enumeration', 't')},
            'beta': {'b': ('integer', 'b'), 't': ('enumeration', 't')}
        }})
