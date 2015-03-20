from scheme import *
from tests.util import *

class TestToken(FieldTestCase):
    def test_processing(self):
        field = Token()
        self.assert_processed(field, None, 'good', 'good.good', 'good-good',
            'good.good-good', 'good:good', 'good:good:good', 'good.good:good.good',
            'good-good:good-good', 'good.good-good:good.good-good', str(uuid4()))
        self.assert_not_processed(field, 'invalid', True, 2, '', 'bad.', '.bad',
            '-bad', 'bad-', ':bad', 'bad:')

    def test_segments(self):
        field = Token(segments=1)
        self.assert_processed(field, 'good', 'good.good', 'good-good', 'good.good-good')
        self.assert_not_processed(field, 'invalid', 'bad:bad', 'bad:bad:bad')

        field = Token(segments=2)
        self.assert_processed(field, 'good:good', 'good.good:good', 'good:good-good')
        self.assert_not_processed(field, 'invalid', 'bad', 'bad.bad', 'bad-bad',
            'bad:bad:bad')

    def test_interpolation(self):
        field = Token()
        self.assert_interpolated(field, None, 'token')
        self.assert_interpolated(field, ('${value}', 'token'), value='token')
