from vn_numberwords import words_to_number, currency_words_to_number


def test_words_to_number_basic():
    """Test basic words to number conversion"""
    assert words_to_number("không") == 0
    assert words_to_number("một") == 1
    assert words_to_number("mười") == 10
    assert words_to_number("mười một") == 11
    assert words_to_number("hai mươi") == 20
    assert words_to_number("hai mươi mốt") == 21


def test_words_to_number_tens():
    """Test tens conversion (10-19)"""
    assert words_to_number("mười") == 10
    assert words_to_number("mười một") == 11
    assert words_to_number("mười hai") == 12
    assert words_to_number("mười ba") == 13
    assert words_to_number("mười bốn") == 14
    assert words_to_number("mười năm") == 15
    assert words_to_number("mười sáu") == 16
    assert words_to_number("mười bảy") == 17
    assert words_to_number("mười tám") == 18
    assert words_to_number("mười chín") == 19


def test_words_to_number_non_accented():
    """Test non-accented Vietnamese words"""
    assert words_to_number("muoi") == 10
    assert words_to_number("muoi mot") == 11
    assert words_to_number("muoi hai") == 12
    assert words_to_number("muoi ba") == 13
    assert words_to_number("muoi bon") == 14
    assert words_to_number("muoi nam") == 15
    assert words_to_number("muoi sau") == 16
    assert words_to_number("muoi bay") == 17
    assert words_to_number("muoi tam") == 18
    assert words_to_number("muoi chin") == 19


def test_words_to_number_hundreds():
    """Test hundreds conversion"""
    assert words_to_number("một trăm") == 100
    assert words_to_number("hai trăm") == 200
    assert words_to_number("một trăm mười") == 110
    assert words_to_number("một trăm mười một") == 111
    assert words_to_number("hai trăm ba mươi tư") == 234


def test_words_to_number_thousands():
    """Test thousands conversion"""
    assert words_to_number("một nghìn") == 1000
    assert words_to_number("một ngàn") == 1000
    assert words_to_number("hai nghìn") == 2000
    assert words_to_number("một nghìn hai trăm") == 1200
    assert words_to_number("một nghìn hai trăm ba mươi tư") == 1234


def test_words_to_number_millions():
    """Test millions conversion"""
    assert words_to_number("một triệu") == 1000000
    assert words_to_number("hai triệu") == 2000000
    assert words_to_number("một triệu hai trăm nghìn") == 1200000
    assert words_to_number("năm trăm triệu") == 500000000


def test_words_to_number_billions():
    """Test billions conversion"""
    assert words_to_number("một tỷ") == 1000000000
    assert words_to_number("hai tỷ") == 2000000000
    assert words_to_number("một tỷ hai trăm triệu") == 1200000000


def test_words_to_number_complex():
    """Test complex numbers with multiple magnitude keywords"""
    # Test with ASCII versions to avoid encoding issues
    assert words_to_number("mot tram nghin ty") == 100000000000000
    assert (
        words_to_number("mot tram nghin ty khong tram ba muoi tu ty") == 100034000000000
    )
    assert (
        words_to_number(
            "mot tram nghin ty khong tram ba muoi tu ty nam tram bon muoi lam trieu bon tram ba muoi lam nghin"
        )
        == 100034545435000
    )


def test_currency_words_to_number():
    """Test currency words to number conversion"""
    assert currency_words_to_number("một nghìn đồng") == 1000
    assert currency_words_to_number("năm trăm triệu đồng") == 500000000
    assert currency_words_to_number("một tỷ đồng") == 1000000000


def test_words_to_number_edge_cases():
    """Test edge cases"""
    assert words_to_number("") == 0  # Empty string
    assert words_to_number("không") == 0  # Zero
    assert words_to_number("một trăm lẻ một") == 101  # With "lẻ"
    assert words_to_number("một trăm linh một") == 101  # With "linh"
