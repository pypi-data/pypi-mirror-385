import datetime
import random
import typing

__all__ = [
    "PersonalCode",
    "generate_aged_latvian_personal_code",
    "generate_random_latvian_personal_code",
]

START_LEGACY_DATE: datetime.date = datetime.date(1923, 1, 1)
FINAL_LEGACY_DATE: datetime.date = datetime.date(2017, 7, 1)


def generate_random_latvian_personal_code(anonymous: bool = False) -> str:
    if anonymous:
        return PersonalCode.generate_anonymous_with_check_digit().dashed
    return PersonalCode.generate_legacy_with_check_digit().dashed


def generate_aged_latvian_personal_code(years: int) -> str:
    return PersonalCode.generate_legacy_with_check_digit(years).dashed


class PersonalCode(typing.NamedTuple):
    first_part: str
    second_part: str
    has_check_digit: bool = False

    @classmethod
    def generate_anonymous_personal_code(cls) -> "PersonalCode":
        pc = f"3{random.randint(2 * 10**9, 10 * 10**9 - 1)}"
        first_part = pc[:6]
        second_part = pc[6:]
        instance = cls(first_part, second_part)
        return instance

    @classmethod
    def generate_anonymous_with_check_digit(cls) -> "PersonalCode":
        tmp = cls.generate_anonymous_personal_code()
        check_digit = tmp._get_checksum_digit()
        if check_digit == 10:  # noqa: PLR2004
            return tmp.generate_anonymous_with_check_digit()
        second_part = tmp.second_part[:-1] + str(check_digit)
        instance = cls(tmp.first_part, second_part, True)
        return instance

    @classmethod
    def generate_legacy_with_check_digit(cls, years: int | None = None) -> "PersonalCode":
        if years is not None:
            if years < (datetime.date.today() - FINAL_LEGACY_DATE).days // 365:
                raise ValueError(
                    "Too young for legacy Personal Code! years < "
                    f"{(datetime.date.today() - FINAL_LEGACY_DATE).days // 365}"
                )
            min_age_in_days = abs(years) * 365
            max_age_in_days = abs(years + 1) * 365
            birthdate = datetime.date.today() - datetime.timedelta(
                days=random.randint(min_age_in_days + 1, max_age_in_days - 1)
            )
        else:
            max_age_in_days = (FINAL_LEGACY_DATE - START_LEGACY_DATE).days
            min_age_in_days = 1
            birthdate = FINAL_LEGACY_DATE - datetime.timedelta(
                days=random.randint(min_age_in_days + 1, max_age_in_days - 1)
            )
        return cls._create_from_birthday(birthdate)

    @classmethod
    def generate_legacy_for_birthday(cls, *args: datetime.date | int) -> "PersonalCode":
        if len(args) == 1:
            if not isinstance(args[0], datetime.date):
                raise ValueError(
                    f"Calling method with one parameter, it must be of type `datetime.date` not `{type(args[0])}`"
                )
            birthday = args[0]
        elif len(args) == 3:  # noqa: PLR2004
            if isinstance(args[0], int) and isinstance(args[1], int) and isinstance(args[2], int):
                birthday = datetime.date(args[0], args[1], args[2])
            else:
                raise ValueError(
                    "When calling method with three parameters, "
                    f"they all must be of type `int` not `{[type(arg) for arg in args]}`"
                )
        else:
            raise ValueError(
                "Method must be called with either one argument which is `datetime.date` or three int parameters "
                "which represent year, month, day representing dates between "
                f"{START_LEGACY_DATE} and {FINAL_LEGACY_DATE}"
            )
        if not START_LEGACY_DATE <= birthday < FINAL_LEGACY_DATE:
            raise ValueError(
                "Legacy non-anonymous personal codes are generated for "
                f"birthdays since {START_LEGACY_DATE} till {FINAL_LEGACY_DATE}!\n"
                f"{START_LEGACY_DATE} <= {birthday} < {FINAL_LEGACY_DATE}"
            )
        return cls._create_from_birthday(birthday)

    @classmethod
    def _create_from_birthday(cls, birthday: datetime.date) -> "PersonalCode":
        first_part = f"{birthday.day:02d}{birthday.month:02d}{str(birthday.year)[2:]}"
        century_digit = 2 if birthday.year // 2000 else 1 if birthday.year // 1900 else 0
        second_part = f"{century_digit}{random.randint(0, 999):03}"
        tmp = cls(first_part, second_part)
        check_digit = tmp._get_checksum_digit()
        if check_digit == 10:  # noqa: PLR2004
            return cls._create_from_birthday(birthday)
        second_part = f"{second_part}{check_digit}"
        return cls(first_part, second_part, True)

    def as_tuple(self) -> tuple[str, str]:
        return self.first_part, self.second_part

    def __str__(self) -> str:
        return f"{self.first_part}{self.second_part}"

    def _get_checksum_digit(self) -> int:
        _factors = [1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        return (1101 - sum(map(lambda p, f: int(p) * f, str(self)[:10], _factors))) % 11

    @property
    def dashed(self) -> str:
        return f"{self.first_part}-{self.second_part}"

    @property
    def is_valid(self) -> bool:
        if not self.is_new_type:
            try:
                _ = self.date_of_birth
            except ValueError:
                return False
        return str(self._get_checksum_digit()) == self.second_part[-1]

    @property
    def date_of_birth(self) -> datetime.date:
        if self.is_new_type:
            raise ValueError("Unable to get date of birth for anonymous personal codes!")
        return datetime.date(
            (1800 if self.second_part[0] == "0" else 1900 if self.second_part[0] == "1" else 2000)
            + int(self.first_part[4:]),
            int(self.first_part[2:4]),
            int(self.first_part[:2]),
        )

    @property
    def is_new_type(self) -> bool:
        return int(self.first_part[:2]) > 31  # noqa: PLR2004
