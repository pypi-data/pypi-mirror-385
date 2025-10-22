from typing import Union


def parse_vietnamese_number(number_str: str) -> Union[int, float]:
    if not isinstance(number_str, str):
        raise ValueError("Input must be a string")

    try:
        dot_count = number_str.count(".")

        if dot_count == 0:
            return int(number_str)
        elif dot_count == 1:
            parts = number_str.split(".")
            if len(parts[1]) == 3 and parts[1].isdigit():
                return int(number_str.replace(".", ""))
            else:
                return float(number_str)
        else:
            parts = number_str.split(".")
            if len(parts[-1]) != 3 or not parts[-1].isdigit():
                integer_part = ".".join(parts[:-1]).replace(".", "")
                decimal_part = parts[-1]
                return float(f"{integer_part}.{decimal_part}")
            else:
                return int(number_str.replace(".", ""))
    except ValueError:
        raise ValueError(f"Invalid number format: {number_str}")


def format_number_with_dots(number: Union[int, float, str]) -> str:
    if isinstance(number, str):
        if "." in number:
            integer_part_str, decimal_part = number.split(".", 1)
            return f"{int(integer_part_str):,}".replace(",", ".") + f".{decimal_part}"
        else:
            return f"{int(number):,}".replace(",", ".")
    elif isinstance(number, float):
        integer_part = int(number)
        decimal_part_str = str(number).split(".")[1] if "." in str(number) else ""
        if decimal_part_str:
            return f"{integer_part:,}".replace(",", ".") + f".{decimal_part_str}"
        else:
            return f"{integer_part:,}".replace(",", ".")
    else:
        return f"{number:,}".replace(",", ".")
