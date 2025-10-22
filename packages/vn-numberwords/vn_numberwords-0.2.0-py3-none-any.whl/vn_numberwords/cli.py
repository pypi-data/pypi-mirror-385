import argparse
from typing import Optional
from . import number_to_words, number_to_currency, SouthDictionary
from .core.interfaces import DictionaryInterface


def main() -> None:
    parser = argparse.ArgumentParser(description="Vietnamese number to words")
    parser.add_argument("number", help="Number or VN formatted string (e.g. 1.234.56)")
    parser.add_argument("--currency", "-c", help="Currency unit (e.g. đồng)")
    parser.add_argument("--south", action="store_true", help="Use Southern dictionary")
    args = parser.parse_args()

    dictionary: Optional[DictionaryInterface] = (
        SouthDictionary() if args.south else None
    )

    if args.currency:
        print(number_to_currency(args.number, args.currency, dictionary))
    else:
        print(number_to_words(args.number, dictionary))


if __name__ == "__main__":
    main()
