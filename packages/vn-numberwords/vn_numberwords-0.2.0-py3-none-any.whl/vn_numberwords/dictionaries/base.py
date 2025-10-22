from ..core.interfaces import DictionaryInterface


class Dictionary(DictionaryInterface):
    TRIPLET_UNITS = [
        "không",
        "một",
        "hai",
        "ba",
        "bốn",
        "năm",
        "sáu",
        "bảy",
        "tám",
        "chín",
    ]

    TRIPLET_TENS = [
        "",
        "mười",
        "hai mươi",
        "ba mươi",
        "bốn mươi",
        "năm mươi",
        "sáu mươi",
        "bảy mươi",
        "tám mươi",
        "chín mươi",
    ]

    HUNDRED = "trăm"

    EXPONENTS = [
        "",
        "nghìn",
        "triệu",
        "tỷ",
        "nghìn tỷ",
        "triệu tỷ",
    ]

    def zero(self) -> str:
        return self.TRIPLET_UNITS[0]

    def minus(self) -> str:
        return "âm"

    def separator(self) -> str:
        return " "

    def triplet_ten_separator(self) -> str:
        return "linh"

    def special_triplet_unit_one(self) -> str:
        return "mốt"

    def special_triplet_unit_four(self) -> str:
        return "bốn"

    def special_triplet_unit_five(self) -> str:
        return "lăm"

    def fraction(self) -> str:
        return "phẩy"

    def get_triplet_unit(self, unit: int) -> str:
        if not (0 <= unit <= 9):
            raise ValueError(f"Unit arg ({unit}) must be in 0-9 range!")
        return self.TRIPLET_UNITS[unit]

    def get_triplet_ten(self, ten: int) -> str:
        if not (0 <= ten <= 9):
            raise ValueError(f"Ten arg ({ten}) must be in 0-9 range!")
        return self.TRIPLET_TENS[ten]

    def get_triplet_hundred(self, hundred: int) -> str:
        if not (0 <= hundred <= 9):
            raise ValueError(f"Hundred arg ({hundred}) must be in 0-9 range!")
        return self.TRIPLET_UNITS[hundred] + self.separator() + self.HUNDRED

    def get_exponent(self, power: int) -> str:
        if not (0 <= power < len(self.EXPONENTS)):
            raise ValueError(f"Power arg ({power}) not exist in vietnamese dictionary!")
        return self.EXPONENTS[power]
