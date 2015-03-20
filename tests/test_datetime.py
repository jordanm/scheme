from scheme import *
from tests.util import *

class TestDateTime(FieldTestCase):
    def test_instantiation(self):
        with self.assertRaises(TypeError):
            DateTime(minimum=True)

        with self.assertRaises(TypeError):
            DateTime(maximum=True)

    def test_processing(self):
        field = DateTime()
        self.assert_processed(field, None)
        self.assert_not_processed(field, 'invalid', True)

        now = datetime.now().replace(microsecond=0)
        now_local = now.replace(tzinfo=LOCAL)
        now_utc = now_local.astimezone(UTC)
        now_text = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

        self.assertEqual(field.process(now_text, INBOUND, True), now_local)
        self.assertEqual(field.process(now, OUTBOUND, True), now_text)
        self.assertEqual(field.process(now_local, OUTBOUND, True), now_text)
        self.assertEqual(field.process(now_utc, OUTBOUND, True), now_text)

    def test_utc_processing(self):
        field = DateTime(utc=True)
        self.assert_processed(field, None)
        self.assert_not_processed(field, 'invalid', True)

        now = datetime.utcnow().replace(microsecond=0)
        now_utc = now.replace(tzinfo=UTC)
        now_text = now_utc.strftime('%Y-%m-%dT%H:%M:%SZ')

        self.assertEqual(field.process(now_text, INBOUND, True), now_utc)
        self.assertEqual(field.process(now, OUTBOUND, True), now_text)
        self.assertEqual(field.process(now_utc, OUTBOUND, True), now_text)

    def test_minimum(self):
        now, now_text = construct_now()
        for field in (DateTime(minimum=now), DateTime(minimum=now_text)):
            self.assertEqual(field.minimum, now)
            self.assert_processed(field, (now, now_text), (now, now_text))
            self.assert_processed(field, (now, now_text), construct_now(+1))
            self.assert_not_processed(field, 'minimum', construct_now(-60))

    def test_maximum(self):
        now, now_text = construct_now()
        for field in (DateTime(maximum=now), DateTime(maximum=now_text)):
            self.assertEqual(field.maximum, now)
            self.assert_processed(field, (now, now_text), (now, now_text))
            self.assert_processed(field, (now, now_text), construct_now(-60))
            self.assert_not_processed(field, 'maximum', construct_now(+60))

    def test_interpolation(self):
        field = DateTime()
        now = datetime.now()

        self.assert_interpolated(field, None, now)
        self.assert_interpolated(field, ('${value}', now), value=now)

    def test_description(self):
        now_text = '2012-01-01T00:00:00Z'

        field = DateTime(name='test', utc=True, minimum=now_text)
        self.assertEqual(field.describe(), {'fieldtype': 'datetime', 'name': 'test',
            'minimum': now_text, 'utc': True})

        field = DateTime(name='test', utc=True, maximum=now_text)
        self.assertEqual(field.describe(), {'fieldtype': 'datetime', 'name': 'test',
            'maximum': now_text, 'utc': True})

        field = DateTime(name='test', utc=True, minimum=now_text, maximum=now_text)
        self.assertEqual(field.describe(), {'fieldtype': 'datetime', 'name': 'test',
            'minimum': now_text, 'maximum': now_text, 'utc': True})
