from .base import Dictionary as BaseDictionary


class SouthDictionary(BaseDictionary):
    EXPONENTS = [
        "",
        "ngàn",
        "triệu",
        "tỷ",
        "ngàn tỷ",
        "triệu tỷ",
    ]

    def triplet_ten_separator(self) -> str:
        return "lẻ"

    def special_triplet_unit_four(self) -> str:
        return "tư"
