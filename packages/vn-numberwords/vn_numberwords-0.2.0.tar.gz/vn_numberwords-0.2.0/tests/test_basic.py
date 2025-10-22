from vn_numberwords import (
    number_to_words,
    number_to_currency,
    vietnamese_string_to_words,
    words_to_number,
    currency_words_to_number,
    SouthDictionary,
)


def test_number_to_words_basic():
    assert number_to_words(0) == "không"
    assert number_to_words(10) == "mười"
    assert number_to_words(21) == "hai mươi mốt"


def test_number_to_words_south():
    assert number_to_words(24, SouthDictionary()) == "hai mươi tư"


def test_currency_and_parse():
    assert number_to_currency(1234, "đồng") == "một nghìn hai trăm ba mươi bốn đồng"
    assert vietnamese_string_to_words("1.234") == "một nghìn hai trăm ba mươi bốn"


def test_plain_integer_input():
    # Integer without dots
    assert number_to_words(123123) == "một trăm hai mươi ba nghìn một trăm hai mươi ba"


def test_plain_string_input():
    # String without dots
    assert (
        vietnamese_string_to_words("123123")
        == "một trăm hai mươi ba nghìn một trăm hai mươi ba"
    )


def test_words_to_number_basic():
    """Test basic words to number conversion"""
    assert words_to_number("mười một") == 11
    assert words_to_number("hai mươi mốt") == 21
    assert words_to_number("một trăm hai mươi ba") == 123
    assert currency_words_to_number("một nghìn đồng") == 1000
