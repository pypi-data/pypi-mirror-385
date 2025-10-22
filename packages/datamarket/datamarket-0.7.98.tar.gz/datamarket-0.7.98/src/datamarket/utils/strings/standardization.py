########################################################################################################################
# IMPORTS

import re
from typing import Literal
from ...params.nominatim import COUNTRY_PARSING_RULES

########################################################################################################################
# FUNCTIONS


def _standardize_es_phone_number(number: str) -> str | None:
    """Standardize phone numbers from Spain using regex validation.

    Args:
        number (str): cleaned, digits-only phone number

    Returns:
        str | None: standardized 9-digit phone number
    """
    # Get the validation regex from params
    pattern = COUNTRY_PARSING_RULES["es"]["phone_validate_pattern"]

    # Validate and extract in one step
    match = pattern.match(number)

    # Return the captured group (the 9-digit number)
    return match.group(1) if match else None


def _standardize_pt_phone_number(number: str) -> str | None:
    """Standardize phone numbers from Portugal using regex validation.

    Args:
        number (str): cleaned, digits-only phone number

    Returns:
        str | None: standardized 9-digit phone number
    """
    # Get the validation regex from params
    pattern = COUNTRY_PARSING_RULES["pt"]["phone_validate_pattern"]

    # Validate and extract in one step
    match = pattern.match(number)

    # Return the captured group (the 9-digit number)
    return match.group(1) if match else None


def parse_phone_number(number: str, country_code: Literal["es", "pt"]) -> str | None:
    """Clean and standardize phone number from a certain country_code

    Args:
        number (str): phone number
        country_code (Literal["es", "pt"]): country code of the phone number to parse

    Raises:
        ValueError: when parsing is not supported for a certain country

    Returns:
        str | None: standardized phone number
    """
    clean_number = re.sub(r"\D", "", number)
    if country_code == "es":
        return _standardize_es_phone_number(clean_number)
    elif country_code == "pt":
        return _standardize_pt_phone_number(clean_number)
    else:
        raise ValueError(f"Country code ({country_code}) is not currently supported")
