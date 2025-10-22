import re
import string

import setech.utils.ssn

__all__ = ["validate_iban", "validate_latvian_personal_code"]


def validate_iban(iban: str) -> bool:
    # Sanitization and sanity check
    _iban = iban.upper().replace(" ", "")
    if not re.search(r"^[A-Z0-9]{10,32}$", _iban):
        return False
    char_map = {str(i): i for i in range(10)}
    char_map.update({char: i for i, char in enumerate(string.ascii_uppercase, start=10)})

    letters = {ord(k): str(v) for k, v in char_map.items()}

    zeros_iban = _iban[:2] + "00" + _iban[4:]
    iban_inverted = zeros_iban[4:] + zeros_iban[:4]
    iban_numbered = iban_inverted.translate(letters)

    verification_chars = 98 - (int(iban_numbered) % 97)

    if f"{int(verification_chars):02}" == _iban[2:4]:
        iban_inverted = _iban[4:] + _iban[:4]
        iban_numbered = iban_inverted.translate(letters)
        return int(iban_numbered) % 97 == 1
    return False


def validate_latvian_personal_code(personal_code: str) -> bool:
    return setech.utils.ssn.PersonalCode(personal_code[:6], personal_code[-5:], True).is_valid
