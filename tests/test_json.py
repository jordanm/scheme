from scheme import *
from tests.util import *

class TestJson(FormatTestCase):
    format = Json

    def test_simple(self):
        self.assert_correct([('test', '"test"')])
