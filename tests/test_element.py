try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from scheme import *

class TestElement(TestCase):
    def test_invalid_schema(self):
        with self.assertRaises(TypeError):
            class Example(Element):
                schema = True

    def test_unnamed_schema(self):
        with self.assertRaises(ValueError):
            class Example(Element):
                schema = Text()

    def test_invalid_polymorphic_inheritor(self):
        with self.assertRaises(ValueError):
            class Example(Element):
                polymorphic_identity = 'test'

    def test_value_element(self):
        class Example(Element):
            schema = Text(nonempty=True, name='value')

        ex = Example(value='test')
        self.assertEqual(ex.value, 'test')

        ex = Example.unserialize('test')
        self.assertIsInstance(ex, Example)
        self.assertEqual(ex.value, 'test')

        ex = ex.serialize()
        self.assertEqual(ex, 'test')

    def test_structural_element(self):
        class Example(Element):
            schema = Structure({
                'name': Text(nonempty=True),
                'description': Text(),
                'important': Boolean(default=False),
            }, nonnull=True)

        ex = Example(name='test')
        self.assertEqual(ex.name, 'test')
        self.assertIs(ex.description, None)
        self.assertEqual(ex.important, False)

        ex = Example.unserialize({'name': 'test', 'description': 'test',
            'important': True})
        self.assertIsInstance(ex, Example)
        self.assertEqual(ex.name, 'test')
        self.assertEqual(ex.description, 'test')
        self.assertEqual(ex.important, True)

        ex = ex.serialize()
        self.assertEqual(ex, {'name': 'test', 'description': 'test',
            'important': True})

    def test_polymorphic_element(self):
        class Example(Element):
            schema = Structure(
                structure={
                    'alpha': {
                        'alpha': Integer(nonempty=True),
                    },
                    'beta': {
                        'beta': Text(nonempty=True),
                    },
                    'gamma': {},
                },
                nonempty=True,
                polymorphic_on='type')

        class Alpha(Example):
            polymorphic_identity = 'alpha'

        class Beta(Example):
            polymorphic_identity = 'beta'

        alpha = Example.unserialize({'type': 'alpha', 'alpha': 1})
        self.assertIsInstance(alpha, Alpha)
        self.assertEqual(alpha.type, 'alpha')
        self.assertEqual(alpha.alpha, 1)

        alpha = alpha.serialize()
        self.assertEqual(alpha, {'type': 'alpha', 'alpha': 1})

        beta = Example.unserialize({'type': 'beta', 'beta': 'beta'})
        self.assertIsInstance(beta, Beta)
        self.assertEqual(beta.type, 'beta')
        self.assertEqual(beta.beta, 'beta')

        beta = beta.serialize()
        self.assertEqual(beta, {'type': 'beta', 'beta': 'beta'})

        gamma = Example.unserialize({'type': 'gamma'})
        self.assertIsInstance(gamma, Example)
        self.assertEqual(gamma.type, 'gamma')

        gamma = gamma.serialize()
        self.assertEqual(gamma, {'type': 'gamma'})

    def test_key_attr(self):
        class Item(Element):
            schema = Text(nonempty=True, name='value')
            key_attr = 'key'

        class Example(Element):
            schema = Structure({
                'items': Map(Item.schema),
            })

        ex = Example.unserialize({'items': {'alpha': 'alpha', 'beta': 'beta'}})
        self.assertIsInstance(ex, Example)
        self.assertIsInstance(ex.items, dict)
        self.assertIn('alpha', ex.items)
        self.assertIn('beta', ex.items)

        alpha = ex.items['alpha']
        self.assertIsInstance(alpha, Item)
        self.assertEqual(alpha.key, 'alpha')
        self.assertEqual(alpha.value, 'alpha')

        beta = ex.items['beta']
        self.assertIsInstance(beta, Item)
        self.assertEqual(beta.key, 'beta')
        self.assertEqual(beta.value, 'beta')

        ex = Example.serialize(ex)
        self.assertEqual(ex, {'items': {'alpha': 'alpha', 'beta': 'beta'}})
