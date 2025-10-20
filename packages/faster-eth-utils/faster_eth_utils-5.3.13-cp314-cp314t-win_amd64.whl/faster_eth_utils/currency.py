import decimal
from decimal import (
    localcontext,
)
from typing import (
    Final,
    Union,
    final,
)

from .types import (
    is_integer,
    is_string,
)
from .units import (
    units,
)


@final
class denoms:
    wei: Final = int(units["wei"])
    kwei: Final = int(units["kwei"])
    babbage: Final = int(units["babbage"])
    femtoether: Final = int(units["femtoether"])
    mwei: Final = int(units["mwei"])
    lovelace: Final = int(units["lovelace"])
    picoether: Final = int(units["picoether"])
    gwei: Final = int(units["gwei"])
    shannon: Final = int(units["shannon"])
    nanoether: Final = int(units["nanoether"])
    nano: Final = int(units["nano"])
    szabo: Final = int(units["szabo"])
    microether: Final = int(units["microether"])
    micro: Final = int(units["micro"])
    finney: Final = int(units["finney"])
    milliether: Final = int(units["milliether"])
    milli: Final = int(units["milli"])
    ether: Final = int(units["ether"])
    kether: Final = int(units["kether"])
    grand: Final = int(units["grand"])
    mether: Final = int(units["mether"])
    gether: Final = int(units["gether"])
    tether: Final = int(units["tether"])


MIN_WEI: Final = 0
MAX_WEI: Final = 2**256 - 1

_NumberType = Union[int, float, str, decimal.Decimal]


def _from_wei(number: int, unit_value: decimal.Decimal) -> Union[int, decimal.Decimal]:
    if number == 0:
        return 0

    if number < MIN_WEI or number > MAX_WEI:
        raise ValueError("value must be between 0 and 2**256 - 1")

    with localcontext() as ctx:
        ctx.prec = 999
        d_number = decimal.Decimal(value=number, context=ctx)
        result_value = d_number / unit_value

    return result_value


def _to_wei(number: _NumberType, unit_value: decimal.Decimal) -> int:
    if is_integer(number) or is_string(number):
        d_number = decimal.Decimal(value=number)  # type: ignore [arg-type]
    elif isinstance(number, float):
        d_number = decimal.Decimal(value=str(number))
    elif isinstance(number, decimal.Decimal):
        d_number = number
    else:
        raise TypeError("Unsupported type. Must be one of integer, float, or string")

    if d_number == decimal.Decimal(0):
        return 0

    s_number = str(number)

    if d_number < 1 and "." in s_number:
        with localcontext() as ctx:
            multiplier = len(s_number) - s_number.index(".") - 1
            ctx.prec = multiplier
            d_number = decimal.Decimal(value=number, context=ctx) * 10**multiplier  # type: ignore [arg-type]
        unit_value /= 10**multiplier

    with localcontext() as ctx:
        ctx.prec = 999
        result_value = decimal.Decimal(value=d_number, context=ctx) * unit_value

    if result_value < MIN_WEI or result_value > MAX_WEI:
        raise ValueError("Resulting wei value must be between 0 and 2**256 - 1")

    return int(result_value)


def from_wei(number: int, unit: str) -> Union[int, decimal.Decimal]:
    """
    Takes a number of wei and converts it to any other ether unit.
    """
    if unit.lower() not in units:
        raise ValueError(f"Unknown unit. Must be one of {'/'.join(units.keys())}")

    unit_value = units[unit.lower()]

    return _from_wei(number, unit_value)


def to_wei(number: _NumberType, unit: str) -> int:
    """
    Takes a number of a unit and converts it to wei.
    """
    if unit.lower() not in units:
        raise ValueError(f"Unknown unit. Must be one of {'/'.join(units.keys())}")

    unit_value = units[unit.lower()]

    return _to_wei(number, unit_value)


def from_wei_decimals(number: int, decimals: int) -> Union[int, decimal.Decimal]:
    """
    Takes a number of wei and converts it to a decimal with the specified
    number of decimals.
    """
    unit_value = decimal.Decimal(10) ** decimal.Decimal(value=decimals)

    return _from_wei(number, unit_value)


def to_wei_decimals(number: _NumberType, decimals: int) -> int:
    """
    Takes a number of a unit and converts it to wei with the specified
    number of decimals.
    """
    unit_value = decimal.Decimal(10) ** decimal.Decimal(value=decimals)

    return _to_wei(number, unit_value)
