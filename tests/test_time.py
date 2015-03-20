from datetime import datetime

from scheme import *
from tests.util import *

class TestTime(FieldTestCase):
    def construct(self, delta=None):
        now = datetime.now().replace(microsecond=0)
        if delta is not None:
            now += timedelta(seconds=delta)

        now = now.time()
        return now, now.strftime('%H:%M:%S')

    def test_invalid_instantiation(self):
        with self.assertRaises(TypeError):
            Time(minimum=True)    
        with self.assertRaises(TypeError):
            Time(maximum=True)

    def test_processing(self):
        field = Time()
        self.assert_processed(field, None, self.construct())
        self.assert_not_processed(field, 'invalid', '')

    def test_minimum(self):
        now, now_text = self.construct()
        for field in (Time(minimum=now), Time(minimum=now_text)):
            self.assertEqual(field.minimum, now)
            self.assert_processed(field, (now, now_text), self.construct(+120))
            self.assert_not_processed(field, 'minimum', self.construct(-120))

    def test_maximum(self):
        now, now_text = self.construct()
        for field in (Time(maximum=now), Time(maximum=now_text)):
            self.assertEqual(field.maximum, now)
            self.assert_processed(field, (now, now_text), self.construct(-120))
            self.assert_not_processed(field, 'maximum', self.construct(+120))

    def test_interpolation(self):
        field = Time()
        now, now_text = self.construct()

        self.assert_interpolated(field, None, now)
        self.assert_interpolated(field, ('${value}', now), value=now)

    def test_description(self):
        now, now_text = self.construct()

        field = Time(name='test', minimum=now_text)
        self.assertEqual(field.describe(), {'fieldtype': 'time', 'name': 'test',
            'minimum': now_text})

        field = Time(name='test', maximum=now_text)
        self.assertEqual(field.describe(), {'fieldtype': 'time', 'name': 'test',
            'maximum': now_text})

        field = Time(name='test', minimum=now_text, maximum=now_text)
        self.assertEqual(field.describe(), {'fieldtype': 'time', 'name': 'test',
            'minimum': now_text, 'maximum': now_text})
