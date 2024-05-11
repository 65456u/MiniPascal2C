from mp2c import Converter
from .test_codes import *


class TestArray:
    def test_array(self):
        converter = Converter()
        success, result = converter(array_test_code)
        assert success
