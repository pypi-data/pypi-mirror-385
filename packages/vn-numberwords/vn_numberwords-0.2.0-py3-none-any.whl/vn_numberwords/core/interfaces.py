from abc import ABC, abstractmethod


class DictionaryInterface(ABC):
    """Interface for Vietnamese number dictionary"""

    @abstractmethod
    def zero(self) -> str:
        pass

    @abstractmethod
    def minus(self) -> str:
        pass

    @abstractmethod
    def separator(self) -> str:
        pass

    @abstractmethod
    def fraction(self) -> str:
        pass

    @abstractmethod
    def special_triplet_unit_one(self) -> str:
        pass

    @abstractmethod
    def special_triplet_unit_four(self) -> str:
        pass

    @abstractmethod
    def special_triplet_unit_five(self) -> str:
        pass

    @abstractmethod
    def triplet_ten_separator(self) -> str:
        pass

    @abstractmethod
    def get_triplet_unit(self, unit: int) -> str:
        pass

    @abstractmethod
    def get_triplet_ten(self, ten: int) -> str:
        pass

    @abstractmethod
    def get_triplet_hundred(self, hundred: int) -> str:
        pass

    @abstractmethod
    def get_exponent(self, power: int) -> str:
        pass
