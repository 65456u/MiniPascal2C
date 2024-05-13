from mp2c import Converter
from .test_codes import *


def test_scope():
    converter = Converter()
    success, result = converter(scope_test_code2, debug = True)
    assert success
