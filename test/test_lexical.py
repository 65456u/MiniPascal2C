from mp2c import Converter
from .test_codes import *


class TestLexical:
    def test_lexical_identifier(self):
        converter = Converter()
        success, result = converter(identifier_test_code)
        assert success

    def test_lexical_keyword(self):
        converter = Converter()
        success, result = converter(keyword_test_code)
        assert success

    def test_lexical_number(self):
        converter = Converter()
        success, result = converter(number_test_code)
        assert success

    def test_lexical_char(self):
        converter = Converter()
        success, result = converter(char_test_code)
        assert not success

    def test_lexical_operator(self):
        converter = Converter()
        success, result = converter(operator_test_code)
        assert result

    def test_lexical_comment(self):
        converter = Converter()
        success, result = converter(comment_test_code)
        assert success
