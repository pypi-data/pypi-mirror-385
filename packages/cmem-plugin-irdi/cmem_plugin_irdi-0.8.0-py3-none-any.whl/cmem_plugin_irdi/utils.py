"""Encode number as base36 encoded string"""


def base_36_encode(number: int) -> str:
    """Return a base36 encoded version of the number

    :param number: a non-negative base 10 integer
    :return: base 36 string
    """
    if number < 0:
        raise ValueError("Number must be non-negative")

    if number == 0:
        return "0"

    encoded: str = ""
    while number > 0:
        number, remainder = divmod(number, 36)
        encoded = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[remainder] + encoded

    return encoded
