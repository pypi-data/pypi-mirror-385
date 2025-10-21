"""A module providing randomish utilities."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache, singledispatch
import re
from typing import Final, NamedTuple, Protocol, Self, cast


class DiceModifier(StrEnum):
    """Standard dice notation formats."""

    STANDARD = "standard"
    ADVANTAGE = "advantage"
    DISADVANTAGE = "disadvantage"


RE_NOTATION: Final = r"(\d+)d(\d+)([+-]\d+)?"
"""Regex pattern for dice notation (e.g., '3d6+2')."""


class DiceProtocol(Protocol):
    """Protocol for dice roll classes."""

    @classmethod
    def roll(cls) -> int:
        """Roll the die and return the result."""
        raise NotImplementedError


class DiceRollMeta(type):
    """Metaclass for dice roll classes."""

    @property
    def dice_sides(cls) -> int:
        """Get the number of sides for the die."""
        name: str = cls.__name__
        if name.startswith("D") and name[1:].isdigit():
            return int(name[1:])
        raise ValueError("sides must be provided or inferred from class name.")


@dataclass(slots=True)
class DiceRollBase(metaclass=DiceRollMeta):
    """Base class for dice rolls."""

    @property
    def sides(self) -> int:
        """Get the number of sides for the die."""
        return type(self).dice_sides

    @classmethod
    def roll(cls) -> int:
        """Roll the die and return the result."""
        from bear_dereth.operations.randoms._rnd import rint  # noqa: PLC0415

        return rint(1, cls.dice_sides)

    def __str__(self) -> str:
        """Return the string representation of the dice roll."""
        return f"d{self.sides}"

    def __repr__(self) -> str:
        """Return the string representation of the dice roll."""
        return f"D{self.sides}(DiceRollBase)"


@dataclass(slots=True)
class D4(DiceRollBase):
    """Class for rolling a four-sided die (D4)."""


@dataclass(slots=True)
class D6(DiceRollBase):
    """Class for rolling a six-sided die (D6)."""


@dataclass(slots=True)
class D10(DiceRollBase):
    """Class for rolling a ten-sided die (D10)."""


@dataclass(slots=True)
class D12(DiceRollBase):
    """Class for rolling a twelve-sided die (D12)."""


@dataclass(slots=True)
class D20(DiceRollBase):
    """Class for rolling a twenty-sided die (D20)."""


@dataclass(slots=True)
class D100(DiceRollBase):
    """Class for rolling a one-hundred-sided die (D100)."""


DICE_CHOICE: dict[int, type[DiceRollBase]] = {
    4: D4,
    6: D6,
    10: D10,
    12: D12,
    20: D20,
    100: D100,
}


def get_custom_dice_class(
    sides: int,
    num: int | None = None,
    modifier: int = 0,
    *,
    dice_notation: str | None = None,
) -> type[DiceRollBase]:
    """Get a custom dice class for non-standard sides.

    Args:
        sides (int): The number of sides on the die.
        num (int | None): The number of dice to roll. Defaults to 1 if not provided.
        modifier (int): The modifier to add to the roll result. Defaults to 0.
        dice_notation (str | None): Optional dice notation string to parse for sides, num, and modifier.


    Returns:
        type[DiceRollBase]: A custom dice class.
    """
    if dice_notation is not None:
        notation: DiceNotation = parse_dice_notation(dice_notation)
        sides = notation.sides
        num = notation.num
        modifier = notation.modifier
    return dataclass(
        type(f"D{sides}", (DiceRollBase,), {"sides": sides, "num": num or 1, "modifier": modifier}), slots=True
    )


@lru_cache(maxsize=1)
def get_compiled_pattern() -> re.Pattern[str]:
    """Get the compiled regex pattern for dice notation.

    Returns:
        re.Pattern[str]: The compiled regex pattern.
    """
    return re.compile(RE_NOTATION, re.IGNORECASE)


def get_match(notation: str) -> re.Match[str] | None:
    """Get the regex match for the dice notation.

    Args:
        notation (str): The dice notation string.

    Returns:
        re.Match[str] | None: The regex match object or None if no match.
    """

    @lru_cache(maxsize=128)
    def _get_match(notation: str) -> re.Match[str] | None:
        pattern: re.Pattern[str] = get_compiled_pattern()
        return pattern.match(notation)

    return _get_match(notation.lower())


class DiceNotation(NamedTuple):
    """Named tuple to represent parsed dice notation."""

    num: int
    sides: int
    modifier: int


def parse_dice_notation(notation: str) -> DiceNotation:
    """Parse dice notation into count, sides, and modifier.

    Example:
        "3d6+2" -> (3, 6, 2)
        "1d20-1" -> (1, 20, -1)
        "2d10"   -> (2, 10, 0)

    Args:
        notation (str): The dice notation string.

    Returns:
        DiceNotationResult: A named tuple containing the number of dice, sides, and modifier.
    """
    match: re.Match[str] | None = get_match(notation)
    if match is None:
        raise ValueError(f"Invalid dice notation: {notation}")

    return DiceNotation(
        num=int(match.group(1)),
        sides=int(match.group(2)),
        modifier=int(match.group(3) or 0),
    )


@singledispatch
def get_dice_type(sides: int | list[int] | str | list[str]) -> type[DiceProtocol] | list[type[DiceProtocol]]:
    """Get the dice type(s) for the given sides.

    Args:
        sides (int | list[int] | str): The number of sides on the die(s) or dice notation.

    Returns:
        type[DiceProtocol] | list[type[DiceProtocol]]: The dice type(s) corresponding to the sides.
    """
    raise TypeError(f"Unsupported type for sides: {type(sides)}")


@get_dice_type.register
def _(sides: int) -> type[DiceProtocol]:
    return (
        type(f"D{sides}", (DiceRollBase,), {"sides": sides})
        if sides not in DICE_CHOICE and sides > 0
        else DICE_CHOICE[sides]
    )


@get_dice_type.register
def _(sides: str) -> type[DiceProtocol]:
    dice_roll: DiceNotation = parse_dice_notation(sides)
    return cast("type[DiceProtocol]", get_dice_type(dice_roll.sides))


@get_dice_type.register
def _(sides: list) -> list[type[DiceProtocol]]:
    dice_types = []
    for side in sides:
        dice_types.append(get_dice_type(side))
    return dice_types


@dataclass(slots=True, frozen=True)
class DiceResult:
    """Class to represent the result of a dice roll."""

    dice_thrown: list[type[DiceProtocol]]
    rolls: list[int]
    total: int

    @property
    def advantage(self) -> int:
        """Return the highest roll (for advantage)."""
        return max(self.rolls)

    @classmethod
    def dice_roll(cls, dice: type[DiceProtocol] | list[type[DiceProtocol]], times: int = 1) -> Self:
        """Roll a list of dice and return the total sum."""
        if not isinstance(dice, list):
            dice = [dice]
        rolls: list[int] = [d.roll() for d in dice for r in range(times)]
        total: int = sum(rolls)
        return cls(dice_thrown=dice, rolls=rolls, total=total)


def rollv(sides: int | list[int] | str | list[str], times: int = 1) -> DiceResult:
    """Roll a variable-sided die a specified number of times.

    Args:
        sides (int | list[int] | str | list[str]): The number of sides on the die(s) or dice notation.
        times (int, optional): The number of times to roll the die. Defaults to 1.

    Returns:
        DiceResult: The result of the dice rolls.
    """
    dice_type: type[DiceProtocol] | list[type[DiceProtocol]] = get_dice_type(sides)
    return DiceResult.dice_roll(dice_type, times=times)


def roll(sides: int, times: int = 1) -> DiceResult:
    """Roll a die with the specified number of sides a given number of times.

    Args:
        sides (int): The number of sides on the die.
        times (int, optional): The number of times to roll the die. Defaults to 1.

    Returns:
        DiceResult: The result of the dice rolls.
    """
    return rollv(sides, times=times)


__all__ = [
    "D4",
    "D6",
    "D10",
    "D12",
    "D20",
    "D100",
    "DiceModifier",
    "DiceNotation",
    "DiceResult",
    "DiceRollBase",
    "get_custom_dice_class",
    "parse_dice_notation",
    "roll",
    "rollv",
]
