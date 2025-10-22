import decimal

__all__ = ["round_decimal"]


def round_decimal(dec: decimal.Decimal, precision: int = 4) -> decimal.Decimal:
    """Round decimal value to a predefined precision from the start of the value. Examples:
        - dec=123456.123456, precision=2 -> 123456.12;
        - dec=123.45678, precision=4 -> 123.4568;
        - dec=123.456, precision=7 -> 123.4560000;
        - dec=123.456, precision=5 -> 123.45600;
        - dec=123.456, precision=3 -> 123.456;
        - dec=123.456, precision=2 -> 123.46;
        - dec=123.456, precision=-1 -> 120;
        - dec=123.456, precision=-2 -> 100;

    :param dec: Decimal value to round
    :param precision: how many digits since the start of the value to keep
    :return: rounded Decimal
    """
    with decimal.localcontext() as ctx:
        ctx.rounding = decimal.ROUND_HALF_UP
        value = decimal.Decimal(dec)
        dec_tuple = dec.as_tuple()
        whole_numbers = len(dec_tuple.digits) + dec_tuple.exponent  # type: ignore[operator]
        ctx.prec = max(1, precision + whole_numbers)
        value = value * 1
    return value
