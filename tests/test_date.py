from scheme import *
from tests.util import *

class TestDate(FieldTestCase):
    def test_invalid_instantiation(self):
        with self.assertRaises(TypeError):
            Date(minimum=True)

        with self.assertRaises(TypeError):
            Date(maximum=True)

    def test_processing(self):
        field = Date()
        self.assert_processed(field, None, construct_today())
        self.assert_not_processed(field, 'invalid', ('', ''))

    def test_minimum(self):
        today, today_text = construct_today()
        for field in (Date(minimum=today), Date(minimum=today_text)):
            self.assertEqual(field.minimum, today)
            self.assert_processed(field, (today, today_text), construct_today(+1))
            self.assert_not_processed(field, 'minimum', construct_today(-1))

    def test_maximum(self):
        today, today_text = construct_today()
        for field in (Date(maximum=today), Date(maximum=today_text)):
            self.assertEqual(field.maximum, today)
            self.assert_processed(field, (today, today_text), construct_today(-1))
            self.assert_not_processed(field, 'maximum', construct_today(+1))

    def test_interpolation(self):
        field = Date()
        today = date.today()

        self.assert_interpolated(field, None, today)
        self.assert_interpolated(field, ('${value}', today), value=today)

    def test_description(self):
        today, today_text = construct_today()

        field = Date(name='test', minimum=today_text)
        self.assertEqual(field.describe(), {'fieldtype': 'date', 'name': 'test',
            'minimum': today_text})

        field = Date(name='test', maximum=today_text)
        self.assertEqual(field.describe(), {'fieldtype': 'date', 'name': 'test',
            'maximum': today_text})

        field = Date(name='test', minimum=today_text, maximum=today_text)
        self.assertEqual(field.describe(), {'fieldtype': 'date', 'name': 'test',
            'minimum': today_text, 'maximum': today_text})
