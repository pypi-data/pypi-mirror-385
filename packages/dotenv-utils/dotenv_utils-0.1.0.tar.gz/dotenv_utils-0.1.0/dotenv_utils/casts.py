"""
This module contains logic for casting string values to native python types.
"""

from datetime import date


def str2bool(value: str) -> bool:
    """
    Parse a string into a boolean value.

    The function recognizes the following strings, case insensitively:

    =======  =======
    True     False
    =======  =======
    "True"   "False"
    "T"      "F"
    "1"      "0"
    "Yes"    "No"
    "Y"      "N"
    =======  =======

    :param value: The boolean string value to parse.
    :raise ValueError: If the string is not a valid (recognized) boolean value.
    :return: The boolean value based on the string content.
    """
    # Normalize the value to lowercase and compare with various possible representations of True and False
    truthy_values = {"true", "t", "1", "yes", "y"}
    falsy_values = {"false", "f", "0", "no", "n"}

    # Normalize input (remove extra spaces and make lowercase)
    value = value.strip().lower()

    if value in truthy_values:
        return True
    elif value in falsy_values:
        return False
    else:
        raise ValueError(f'Invalid boolean value for "{value}". '
                         f'Expected one of: {", ".join(truthy_values)} or {", ".join(falsy_values)}.')


def str2date(value: str) -> date:
    """This is just an alias for ``datetime.date.fromisoformat``."""
    return date.fromisoformat(value)
