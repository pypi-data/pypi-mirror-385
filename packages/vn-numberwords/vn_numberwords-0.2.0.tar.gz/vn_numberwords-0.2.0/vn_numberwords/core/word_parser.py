from typing import Union, List, Optional
import re

from .interfaces import DictionaryInterface
from ..dictionaries.base import Dictionary


class WordToNumberParser:
    """Parser for converting Vietnamese words to numbers - Based on word2number approach"""

    def __init__(self, dictionary: Optional[DictionaryInterface] = None):
        self.dictionary = dictionary or Dictionary()
        self._build_mappings()

    def _build_mappings(self):
        """Build mappings from words to numbers and keywords"""
        # Units mapping (0-9)
        self.units_map = {
            "không": 0,
            "một": 1,
            "mốt": 1,
            "hai": 2,
            "ba": 3,
            "bốn": 4,
            "tư": 4,
            "năm": 5,
            "lăm": 5,
            "nhăm": 5,
            "sáu": 6,
            "bảy": 7,
            "tám": 8,
            "chín": 9,
            # Non-accented versions
            "khong": 0,
            "mot": 1,
            "bon": 4,
            "nam": 5,
            "lam": 5,
            "tu": 4,
            "sau": 6,
            "bay": 7,
            "tam": 8,
            "chin": 9,
        }

        # Special tens mapping
        self.tens_special_map = {"mười": 10, "muoi": 10, "mươi": 10}

        # Keyword mappings (including accented versions)
        self.billion_words = frozenset(("tỷ", "tỏi", "tỉ", "ty"))
        self.million_words = frozenset(("triệu", "củ", "chai", "trieu"))
        self.thousand_words = frozenset(("nghìn", "nghàn", "ngàn", "cành", "nghin"))
        self.hundreds_words = frozenset(("trăm", "lít", "lốp", "xị", "tram"))
        self.tens_words = frozenset(("mươi", "chục", "muoi"))
        self.special_words = frozenset(("lẽ", "linh", "lẻ", "le"))

        # All multiplier words
        self.multiplier_words = self.billion_words.union(
            self.million_words,
            self.thousand_words,
            self.hundreds_words,
            self.tens_words,
            self.special_words,
        )

        # All allowed words (including accented versions)
        self.allowed_words = self.multiplier_words.union(
            set(self.units_map.keys())
        ).union(set(self.tens_special_map.keys()))

        # Add accented versions to allowed words
        accented_units = {
            "không",
            "một",
            "mốt",
            "hai",
            "ba",
            "bốn",
            "tư",
            "năm",
            "lăm",
            "nhăm",
            "sáu",
            "bảy",
            "tám",
            "chín",
        }
        accented_tens = {"mười", "mươi"}
        accented_hundreds = {"trăm"}
        accented_thousands = {"nghìn", "nghàn", "ngàn"}
        accented_millions = {"triệu"}
        accented_billions = {"tỷ", "tỏi", "tỉ"}
        accented_special = {"lẽ", "linh", "lẻ"}

        self.allowed_words = self.allowed_words.union(
            accented_units,
            accented_tens,
            accented_hundreds,
            accented_thousands,
            accented_millions,
            accented_billions,
            accented_special,
        )

    def _normalize_text(self, text: str) -> str:
        """Normalize Vietnamese text for parsing"""
        # Remove punctuation but keep Vietnamese diacritics
        text = re.sub(r"[^\w\s\u00C0-\u1EF9]", " ", text.strip().lower())
        text = re.sub(r"\s+", " ", text)
        return text

    def _split_words(self, text: str) -> List[str]:
        """Split text into words"""
        words = text.split()
        return [word for word in words if word in self.allowed_words]

    def parse_words(self, text: Union[str, List[str]]) -> Union[int, float]:
        """Parse Vietnamese words to number"""
        if isinstance(text, list):
            words = text
        else:
            normalized_text = self._normalize_text(text)
            words = self._split_words(normalized_text)

        if not words:
            return 0

        # Check for negative
        is_negative = False
        if words[0] in ["am", "âm"]:
            is_negative = True
            words = words[1:]

        # Check for zero
        if len(words) == 1 and words[0] in ["khong", "không"]:
            return 0

        # Parse the number
        result = self._parse_large_number_final(words)

        return -result if is_negative else result

    def _parse_large_number(self, words: List[str]) -> int:
        """Parse large numbers by finding keywords and processing segments"""
        # Find all keyword positions with their types
        keyword_positions = []

        for i, word in enumerate(words):
            if word in self.billion_words:
                keyword_positions.append((i, "billion"))
            elif word in self.million_words:
                keyword_positions.append((i, "million"))
            elif word in self.thousand_words:
                keyword_positions.append((i, "thousand"))

        # If no keywords, parse as simple number
        if not keyword_positions:
            return self._parse_hundreds(words)

        # Sort by position
        keyword_positions.sort(key=lambda x: x[0])

        # Process segments based on keyword positions
        segments = []
        start = 0

        for pos, keyword_type in keyword_positions:
            segment = words[start:pos]
            segments.append((segment, keyword_type))
            start = pos + 1

        # Add remaining words (only if there are any and no keywords)
        if start < len(words):
            remaining_words = words[start:]
            # Check if remaining words contain any keywords
            has_keywords = any(
                word
                in self.billion_words.union(self.million_words, self.thousand_words)
                for word in remaining_words
            )
            if not has_keywords:
                segments.append((remaining_words, "units"))

        # Calculate total
        total = 0
        for segment_words, segment_type in segments:
            if segment_words:
                segment_value = self._parse_hundreds(segment_words)
                if segment_type == "billion":
                    total += segment_value * 1000000000
                elif segment_type == "million":
                    total += segment_value * 1000000
                elif segment_type == "thousand":
                    total += segment_value * 1000
                else:
                    total += segment_value
            # Skip empty segments

        return total

    def _parse_large_number_v2(self, words: List[str]) -> int:
        """Parse large numbers with correct handling of compound units"""
        # Find all keyword positions with their types
        keyword_positions = []

        for i, word in enumerate(words):
            if word in self.billion_words:
                keyword_positions.append((i, "billion"))
            elif word in self.million_words:
                keyword_positions.append((i, "million"))
            elif word in self.thousand_words:
                keyword_positions.append((i, "thousand"))

        # If no keywords, parse as simple number
        if not keyword_positions:
            return self._parse_hundreds(words)

        # Sort by position
        keyword_positions.sort(key=lambda x: x[0])

        # Process segments based on keyword positions
        segments = []
        start = 0

        for pos, keyword_type in keyword_positions:
            segment = words[start:pos]
            segments.append((segment, keyword_type))
            start = pos + 1

        # Add remaining words (only if there are any and no keywords)
        if start < len(words):
            remaining_words = words[start:]
            # Check if remaining words contain any keywords
            has_keywords = any(
                word
                in self.billion_words.union(self.million_words, self.thousand_words)
                for word in remaining_words
            )
            if not has_keywords:
                segments.append((remaining_words, "units"))

        # Calculate total
        total = 0
        for segment_words, segment_type in segments:
            if segment_words:
                segment_value = self._parse_hundreds(segment_words)
                if segment_type == "billion":
                    total += segment_value * 1000000000
                elif segment_type == "million":
                    total += segment_value * 1000000
                elif segment_type == "thousand":
                    total += segment_value * 1000
                else:
                    total += segment_value
            # Skip empty segments

        return total

    def _parse_large_number_correct(self, words: List[str]) -> int:
        """Parse large numbers with correct Vietnamese understanding"""
        # Find all keyword positions with their types
        keyword_positions = []

        for i, word in enumerate(words):
            if word in self.billion_words:
                keyword_positions.append((i, "billion"))
            elif word in self.million_words:
                keyword_positions.append((i, "million"))
            elif word in self.thousand_words:
                keyword_positions.append((i, "thousand"))

        # If no keywords, parse as simple number
        if not keyword_positions:
            return self._parse_hundreds(words)

        # Sort by position
        keyword_positions.sort(key=lambda x: x[0])

        # Process segments based on keyword positions
        segments = []
        start = 0

        for pos, keyword_type in keyword_positions:
            segment = words[start:pos]
            segments.append((segment, keyword_type))
            start = pos + 1

        # Add remaining words (only if there are any and no keywords)
        if start < len(words):
            remaining_words = words[start:]
            # Check if remaining words contain any keywords
            has_keywords = any(
                word
                in self.billion_words.union(self.million_words, self.thousand_words)
                for word in remaining_words
            )
            if not has_keywords:
                segments.append((remaining_words, "units"))

        # Calculate total
        total = 0
        for segment_words, segment_type in segments:
            if segment_words:
                segment_value = self._parse_hundreds(segment_words)
                if segment_type == "billion":
                    total += segment_value * 1000000000
                elif segment_type == "million":
                    total += segment_value * 1000000
                elif segment_type == "thousand":
                    total += segment_value * 1000
                else:
                    total += segment_value
            # Skip empty segments

        return total

    def _parse_large_number_final(self, words: List[str]) -> int:
        """Parse large numbers with correct Vietnamese understanding - Final version"""
        # Find all keyword positions with their types and multipliers
        keyword_positions = []

        for i, word in enumerate(words):
            if word in self.billion_words:
                keyword_positions.append((i, "billion", 1000000000))
            elif word in self.million_words:
                keyword_positions.append((i, "million", 1000000))
            elif word in self.thousand_words:
                keyword_positions.append((i, "thousand", 1000))

        # If no keywords, parse as simple number
        if not keyword_positions:
            return self._parse_hundreds(words)

        # Sort by position
        keyword_positions.sort(key=lambda x: x[0])

        # Group consecutive keywords together
        # For example: "mot tram nghin ty" should group "nghin ty" together
        grouped_segments = []
        i = 0

        while i < len(keyword_positions):
            pos, ktype, multiplier = keyword_positions[i]

            # Check if next keyword is consecutive (empty segment between them)
            consecutive_multiplier = multiplier
            j = i + 1

            while j < len(keyword_positions):
                next_pos, next_ktype, next_mult = keyword_positions[j]
                # If next keyword is right after current one (no words between)
                if next_pos == pos + 1:
                    consecutive_multiplier *= next_mult
                    pos = next_pos
                    j += 1
                else:
                    break

            # Add the grouped segment
            if i == 0:
                segment_start = 0
            else:
                segment_start = keyword_positions[i - 1][0] + 1

            segment = words[segment_start : keyword_positions[i][0]]
            grouped_segments.append((segment, consecutive_multiplier))

            i = j

        # Add remaining words after last keyword
        if keyword_positions:
            last_pos = keyword_positions[-1][0]
            if last_pos + 1 < len(words):
                remaining = words[last_pos + 1 :]
                has_keywords = any(
                    word
                    in self.billion_words.union(self.million_words, self.thousand_words)
                    for word in remaining
                )
                if not has_keywords:
                    grouped_segments.append((remaining, 1))

        # Calculate total
        total = 0
        for segment_words, multiplier in grouped_segments:
            if segment_words:
                segment_value = self._parse_hundreds(segment_words)
                total += segment_value * multiplier

        return total

    def _parse_hundreds(self, words: List[str]) -> int:
        """Parse hundreds, tens, and units"""
        if not words:
            return 0

        # Check if this segment contains large number keywords
        if any(
            word in self.billion_words.union(self.million_words, self.thousand_words)
            for word in words
        ):
            return self._parse_large_number(words)

        # Find keyword positions within hundreds
        keyword_positions = {}

        for i, word in enumerate(words):
            if word in self.hundreds_words:
                keyword_positions["hundreds"] = i
            elif word in self.tens_words:
                keyword_positions["tens"] = i
            elif word in self.tens_special_map:
                keyword_positions["tens"] = i

        # Handle special case with "lẻ/linh"
        if any(word in self.special_words for word in words):
            return self._parse_with_special_words(words)

        # Parse based on keyword positions
        if "hundreds" in keyword_positions:
            hundreds_pos = keyword_positions["hundreds"]
            hundreds_value = (
                self.units_map.get(words[hundreds_pos - 1], 0)
                if hundreds_pos > 0
                else 1
            )
            remaining_words = words[hundreds_pos + 1 :]
            tens_value = self._parse_tens(remaining_words)
            return hundreds_value * 100 + tens_value

        elif "tens" in keyword_positions:
            return self._parse_tens(words)

        else:
            # Simple units
            if len(words) == 1:
                return self.units_map.get(words[0], 0)
            else:
                # Multiple units - treat as individual digits
                result = 0
                for word in words:
                    result = result * 10 + self.units_map.get(word, 0)
                return result

    def _parse_tens(self, words: List[str]) -> int:
        """Parse tens and units"""
        if not words:
            return 0

        if len(words) == 1:
            # Check special tens first
            if words[0] in self.tens_special_map:
                return self.tens_special_map[words[0]]
            return self.units_map.get(words[0], 0)

        # Check for "mười" + unit pattern
        if len(words) == 2 and words[0] in self.tens_special_map:
            return self.tens_special_map[words[0]] + self.units_map.get(words[1], 0)

        # Find tens keyword
        tens_pos = None
        for i, word in enumerate(words):
            if word in self.tens_words:
                tens_pos = i
                break

        if tens_pos is not None:
            tens_value = (
                self.units_map.get(words[tens_pos - 1], 1) if tens_pos > 0 else 1
            )
            remaining_words = words[tens_pos + 1 :]
            units_value = (
                self.units_map.get(remaining_words[0], 0) if remaining_words else 0
            )
            return tens_value * 10 + units_value

        # No tens keyword - treat as individual units
        result = 0
        for word in words:
            result = result * 10 + self.units_map.get(word, 0)
        return result

    def _parse_with_special_words(self, words: List[str]) -> int:
        """Parse numbers with special words like 'lẻ/linh'"""
        total = 0
        current_segment: List[str] = []

        for word in words:
            if word in self.special_words:
                if current_segment:
                    total += self._parse_hundreds(current_segment)
                    current_segment = []
            else:
                current_segment.append(word)

        if current_segment:
            total += self._parse_hundreds(current_segment)

        return total

    def parse_currency_words(
        self, text: Union[str, List[str]], currency_unit: str = "đồng"
    ) -> Union[int, float]:
        """Parse Vietnamese currency words to number"""
        if isinstance(text, list):
            words = text
        else:
            normalized_text = self._normalize_text(text)
            words = self._split_words(normalized_text)

        # Remove currency unit from the end
        if words and words[-1] == currency_unit:
            words = words[:-1]

        return self.parse_words(words)
