from typing import Union, List, Tuple, Optional

from .interfaces import DictionaryInterface
from ..dictionaries.base import Dictionary


class NumberTransformer:
    """Main class for converting numbers to Vietnamese words"""

    def __init__(
        self,
        dictionary: Optional[DictionaryInterface] = None,
        decimal_part: Optional[int] = None,
    ):
        self.dictionary = dictionary or Dictionary()
        self.decimal_part = decimal_part

    def collapse_words(self, words: List[str]) -> str:
        separator = self.dictionary.separator()
        words = [word for word in words if word]
        return separator.join(words)

    def resolve_number(self, number: Union[int, float, str]) -> Tuple[bool, int, int]:
        if (
            not isinstance(number, (int, float, str))
            or not str(number).replace("-", "").replace(".", "").isdigit()
        ):
            raise ValueError(f"Number arg ({number}) must be numeric!")

        if self.decimal_part is None:
            number = float(number)
            number = str(number)
        else:
            number = f"{float(number):.{self.decimal_part}f}"

        is_negative = number.startswith("-")

        if "." in number:
            parts = number.split(".", 1)
            integer_part = int(parts[0].lstrip("-"))
            decimal_part = int(parts[1])
        else:
            integer_part = int(number.lstrip("-"))
            decimal_part = 0

        return is_negative, integer_part, decimal_part

    def split_triplet(self, triplet: int) -> tuple:
        hundred = (triplet // 100) % 10
        ten = (triplet // 10) % 10
        unit = triplet % 10
        return hundred, ten, unit

    def get_triplet_unit(self, unit: int, ten: int) -> str:
        if 1 <= ten <= 5 and unit == 5:
            return self.dictionary.special_triplet_unit_five()

        if ten >= 2:
            if unit == 1:
                return self.dictionary.special_triplet_unit_one()
            if unit == 4:
                return self.dictionary.special_triplet_unit_four()

        return self.dictionary.get_triplet_unit(unit)

    def triplet_to_words(self, triplet: int, is_first: bool, exponent: int) -> str:
        hundred, ten, unit = self.split_triplet(triplet)
        words = []

        if hundred > 0 or not is_first:
            words.append(self.dictionary.get_triplet_hundred(hundred))

            if ten == 0 and unit > 0:
                words.append(self.dictionary.triplet_ten_separator())

        if ten > 0:
            words.append(self.dictionary.get_triplet_ten(ten))

        if unit > 0:
            words.append(self.get_triplet_unit(unit, ten))

        words.append(self.dictionary.get_exponent(exponent))

        return self.collapse_words(words)

    def number_to_triplets(self, number: int) -> List[int]:
        triplets: List[int] = []

        while number > 0:
            triplets.insert(0, number % 1000)
            number = number // 1000

        return triplets

    def to_words(self, number: Union[int, float, str]) -> str:
        is_negative, integer_part, decimal_part = self.resolve_number(number)
        words = []

        if is_negative:
            words.append(self.dictionary.minus())

        if integer_part == 0:
            words.append(self.dictionary.zero())

        triplets = self.number_to_triplets(integer_part)

        for pos, triplet in enumerate(triplets):
            if triplet > 0:
                words.append(
                    self.triplet_to_words(triplet, pos == 0, len(triplets) - pos - 1)
                )

        if decimal_part > 0:
            words.append(self.dictionary.fraction())
            words.append(self.to_words(decimal_part))

        return self.collapse_words(words)

    def to_currency(
        self, number: Union[int, float, str], unit: Union[str, List[str]] = "đồng"
    ) -> str:
        if isinstance(unit, str):
            unit = [unit]

        is_negative, integer_part, decimal_part = self.resolve_number(number)

        if decimal_part == 0 or len(unit) < 2:
            words = [self.to_words(number), unit[0]]
        else:
            main_unit, decimal_unit = unit[0], unit[1]
            words = []
            if is_negative:
                words.append(self.dictionary.minus())
            words.append(self.to_words(integer_part))
            words.append(main_unit)
            words.append(self.to_words(decimal_part))
            words.append(decimal_unit)

        return self.collapse_words(words)
