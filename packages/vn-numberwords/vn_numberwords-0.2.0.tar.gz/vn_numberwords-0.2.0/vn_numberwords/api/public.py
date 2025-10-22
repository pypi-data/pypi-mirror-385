from typing import Union, List, Optional

from ..core.interfaces import DictionaryInterface
from ..core.transformer import NumberTransformer
from ..core.word_parser import WordToNumberParser
from ..core.utils import parse_vietnamese_number


def number_to_words(
    number: Union[int, float, str], dictionary: Optional[DictionaryInterface] = None
) -> str:
    transformer = NumberTransformer(dictionary)
    return transformer.to_words(number)


def number_to_currency(
    number: Union[int, float, str],
    unit: Union[str, List[str]] = "đồng",
    dictionary: Optional[DictionaryInterface] = None,
) -> str:
    transformer = NumberTransformer(dictionary)
    return transformer.to_currency(number, unit)


def vietnamese_string_to_words(
    number_str: str, dictionary: Optional[DictionaryInterface] = None
) -> str:
    number = parse_vietnamese_number(number_str)
    return number_to_words(number, dictionary)


def vietnamese_string_to_currency(
    number_str: str,
    unit: Union[str, List[str]] = "đồng",
    dictionary: Optional[DictionaryInterface] = None,
) -> str:
    number = parse_vietnamese_number(number_str)
    return number_to_currency(number, unit, dictionary)


def words_to_number(
    words: Union[str, List[str]], dictionary: Optional[DictionaryInterface] = None
) -> Union[int, float]:
    """Convert Vietnamese words to number"""
    parser = WordToNumberParser(dictionary)
    return parser.parse_words(words)


def currency_words_to_number(
    words: Union[str, List[str]],
    currency_unit: str = "đồng",
    dictionary: Optional[DictionaryInterface] = None,
) -> Union[int, float]:
    """Convert Vietnamese currency words to number"""
    parser = WordToNumberParser(dictionary)
    return parser.parse_currency_words(words, currency_unit)
