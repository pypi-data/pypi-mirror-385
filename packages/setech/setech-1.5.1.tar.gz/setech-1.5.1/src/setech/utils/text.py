import datetime
import decimal
import re

import num2words  # type: ignore[import-untyped]
import unidecode

from setech.constants import LATVIAN_MONTH_MAP_ACU, LATVIAN_MONTH_MAP_NOM

__all__ = ["convert_datetime_to_latvian_words", "convert_number_to_latvian_words", "slugify", "transliterate"]


def convert_number_to_latvian_words(number: decimal.Decimal, with_currency: bool = True) -> str:
    """Convert a number into words in Latvian language."""
    if not number:
        return ""

    whole_part = int(number)
    fraction_part = round((number - whole_part) * 100)
    text = num2words.num2words(whole_part, lang="lv")

    if with_currency:
        text += f" eiro, {fraction_part:02d} centi"
    else:
        text += f", {fraction_part:02d}"

    if whole_part in [100, 1000]:
        text = "viens " + text

    return text


def convert_datetime_to_latvian_words(date: datetime.date | None = None, accusative: bool = False) -> str:
    """
    Convert a date into words in Latvian.
    :param date: date to convert or today's date if None
    :param accusative: return string in either accusative form (true) or nominative
    :return:
    """
    if date is None:
        date = datetime.date.today()
    date_sign_contract = date.strftime("%Y. gada %d. ")
    date_sign_contract += (LATVIAN_MONTH_MAP_ACU if accusative else LATVIAN_MONTH_MAP_NOM)[date.month]
    return date_sign_contract


def transliterate(value: str) -> str:
    """
    Convert Unicode characters to ASCII only characters
    :param value:
    :return:
    """
    return unidecode.unidecode(value).strip()


def slugify(value: str, *, glue: str = "-") -> str:
    """
    Convert to ASCII. Convert spaces or repeated dashes to single dashes.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace,
    dashes, and underscores.
    :param value: string to slugify
    :param glue: character to use for whitespace character replacement
    :return: slugified string
    """
    return re.sub(r"[-\s]+", glue, re.sub(r"[^\w\s-]", "", transliterate(str(value)).lower())).strip("-_")
