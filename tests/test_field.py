from scheme import *
from tests.util import *

class TestField(FieldTestCase):
    def test_construction(self):
        field = Field(nonempty=True)
        self.assertTrue(field.required and field.nonnull)

        field = Field(custom_attr=True)
        self.assertTrue(field.custom_attr)

        field = Field(_not_custom_attr=True)
        self.assertIs(field._not_custom_attr, None)

        field = Field(instantiator='tests.util.attrmap')
        self.assertIs(field.instantiator, attrmap)

        field = Field(extractor='tests.util.attrmap')
        self.assertIs(field.extractor, attrmap)

        def preprocess(value):
            return value

        field = Field(preprocessor=preprocess)
        self.assertIs(field.preprocessor, preprocess)

        field = Field()
        self.assertEqual(field.guaranteed_name, '(field)')

        field = Field(name='name')
        self.assertEqual(field.guaranteed_name, 'name')

    def test_nulls(self):
        field = Field()
        for phase in (INBOUND, OUTBOUND):
            self.assert_processed(field, phase)

        field = Field(nonnull=True)
        self.assert_not_processed(field, 'nonnull', None)

    def test_clone(self):
        stuff = {'a': 1, 'b': 2}
        field = Field(name='field', stuff=stuff)

        cloned = field.clone(extra=True)
        self.assertIsNot(field, cloned)
        self.assertEqual(field.stuff, cloned.stuff)
        self.assertIsNot(field.stuff, cloned.stuff)
        self.assertEqual(cloned.name, 'field')
        self.assertEqual(cloned.extra, True)

        cloned = field.clone(default='default')
        self.assertIsNot(field, cloned)
        self.assertEqual(cloned.default, 'default')

        class cannot_be_deepcopied(object):
            def __deepcopy__(self, memo):
                raise TypeError()

        field = Field(name='test', description=cannot_be_deepcopied())
        cloned = field.clone()
        self.assertEqual(cloned.name, 'test')
        self.assertIsNone(cloned.description)

    def test_describe(self):
        field = Field(name='test', required=True, aspects={'empty_custom_attr': None},
            custom_attr=True)
        self.assertEqual(field.describe(), {'fieldtype': 'field',
            'name': 'test', 'required': True, 'custom_attr': True})
        self.assertEqual(field.describe(custom_param=True), {'fieldtype': 'field',
            'name': 'test', 'required': True, 'custom_attr': True,
            'custom_param': True})

        field = Field(custom_attr=object())
        self.assertEqual(field.describe(), {'fieldtype': 'field'})
        self.assertEqual(field.describe(custom_param=object()), {'fieldtype': 'field'})

        class cannot_be_described(object):
            pass

        field = Field(name='test', cannot_be_described=cannot_be_described())
        self.assertEqual(field.describe({'name': None, 'cannot_be_described': None}),
            {'fieldtype': 'field', 'name': 'test'})

    def test_extraction(self):
        field = Field()
        self.assertIs(field.extract(None), None)
        self.assertEqual(field.extract(1), 1)

        with self.assertRaises(FieldExcludedError):
            field.extract(1, required=True)

        def bad_extractor(*args):
            raise TypeError()

        field = Field(extractor=bad_extractor)
        with self.assertRaises(CannotExtractError):
            field.extract(1)

    def test_filter(self):
        field = Field(one=True, two=False)

        self.assertIs(field.filter(False), field)
        self.assertIs(field.filter(True), field)

        self.assertIs(field.filter(False, one=True), field)
        self.assertIs(field.filter(True, one=True), field)
        self.assertIsNone(field.filter(False, one=False))
        self.assertIsNone(field.filter(True, one=False))

        self.assertIs(field.filter(False, one=False, two=False), field)
        self.assertIsNone(field.filter(True, one=False, two=False), field)
        self.assertIs(field.filter(False, one=True, two=False), field)
        self.assertIs(field.filter(True, one=True, two=False), field)

    def test_naive_instantiation(self):
        field = Field()
        self.assertEqual(field.instantiate(1), 1)

    def test_interpolation(self):
        field = Field()
        self.assertEqual(field.interpolate(None, {}), None)

    def test_reconstruction(self):
        with self.assertRaises(ValueError):
            Field.reconstruct({})

        field = Field(name='test', required=True)
        description = field.describe()
        field2 = Field.reconstruct(description)

        self.assertIsNot(field, field2)
        self.assertIsInstance(field2, Field)
        self.assertEqual(field2.name, 'test')
        self.assertTrue(field2.required)

        field3 = Field.reconstruct(field)
        self.assertIs(field3, field)

        field = Field(name='test', value_list=[1, 2, 3], value_tuple=(1, 2, 3),
            custom_field=Field(name='custom'))
        description = field.describe()
        field2 = Field.reconstruct(description)

        self.assertIsNot(field, field2)
        self.assertEqual(field.value_list, [1, 2, 3])
        self.assertEqual(field.value_tuple, (1, 2, 3))
        self.assertIsInstance(field2.custom_field, Field)
        self.assertIsNot(field2.custom_field, field.custom_field)

        bad_specification = {'fieldtype': 'unknown', 'name': 'bad'}
        with self.assertRaises(ValueError):
            Field.reconstruct(bad_specification)

    def test_indirect_instantiation_via_reconstruct(self):
        field = Field.reconstruct('field', name='test', required=True)

        self.assertIsInstance(field, Field)
        self.assertEqual(field.name, 'test')
        self.assertTrue(field.required)

    def test_screen(self):
        field = Field(name='test', required=True)
        self.assertTrue(field.screen())
        self.assertTrue(field.screen(required=None))
        self.assertTrue(field.screen(required=True))
        self.assertFalse(field.screen(required=False))

    def test_transform(self):
        def _transform(value):
            if value.name == 'should_transform':
                return Field(name='transformed')
            else:
                return False

        field = Field(name='should_transform').transform(_transform)
        self.assertEqual(field.name, 'transformed')

        field = Field(name='should_not_transform').transform(_transform)
        self.assertEqual(field.name, 'should_not_transform')

    def test_visit(self):
        def visit(f):
            return f['fieldtype']

        field = Field()
        self.assertEqual(Field.visit(field.describe(), visit), {})
