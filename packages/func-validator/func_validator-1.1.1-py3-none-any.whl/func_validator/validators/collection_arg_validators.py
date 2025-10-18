from operator import contains
from typing import Callable, Container, Iterable, Sized

from ._core import Number, T, ValidationError, Validator
from .numeric_arg_validators import (
    MustBeBetween,
    MustBeEqual,
    MustBeGreaterThan,
    MustBeGreaterThanOrEqual,
    MustBeLessThan,
    MustBeLessThanOrEqual,
)


def _iterable_len_validator(
    arg_values: Sized,
    arg_name: str,
    /,
    *,
    func: Callable,
):
    func(len(arg_values), arg_name)


def _iterable_values_validator(
    values: Iterable,
    arg_name: str,
    /,
    *,
    func: Callable,
):
    for value in values:
        func(value, arg_name)


# Membership and range validation functions


def _must_be_member_of(arg_value, arg_name: str, /, *, value_set: Container):
    if not contains(value_set, arg_value):
        raise ValidationError(
            f"{arg_name}:{arg_value} must be in {value_set!r}"
        )


class MustBeMemberOf(Validator):

    def __init__(self, value_set: Container):
        """Validates that the value is a member of the specified set.

        :param value_set: The set of values to validate against.
                          `value_set` must support the `in` operator.
        """
        self.value_set = value_set

    def __call__(self, arg_value: T, arg_name: str):
        _must_be_member_of(arg_value, arg_name, value_set=self.value_set)


# Size validation functions


class MustBeEmpty(Validator):

    def __call__(self, arg_value: Sized, arg_name: str, /):
        """Validates that the iterable is empty."""
        if len(arg_value) != 0:
            raise ValidationError(f"{arg_name}:{arg_value} must be empty.")


class MustBeNonEmpty(Validator):

    def __call__(self, arg_value: Sized, arg_name: str, /):
        """Validates that the iterable is not empty."""
        if len(arg_value) == 0:
            raise ValidationError(f"{arg_name}:{arg_value} must not be empty.")


class MustHaveLengthEqual(Validator):
    """Validates that the iterable has length equal to the specified
    value.
    """

    def __init__(self, value: int):
        self.value = value

    def __call__(self, arg_value: Sized, arg_name: str):
        _iterable_len_validator(
            arg_value, arg_name, func=MustBeEqual(self.value)
        )


class MustHaveLengthGreaterThan(Validator):
    """Validates that the iterable has length greater than the specified
    value.
    """

    def __init__(self, value: int):
        self.value = value

    def __call__(self, arg_value: Sized, arg_name: str):
        _iterable_len_validator(
            arg_value, arg_name, func=MustBeGreaterThan(self.value)
        )


class MustHaveLengthGreaterThanOrEqual(Validator):
    """Validates that the iterable has length greater than or equal to
    the specified value.
    """

    def __init__(self, value: int):
        self.value = value

    def __call__(self, arg_value: Sized, arg_name: str):
        _iterable_len_validator(
            arg_value, arg_name, func=MustBeGreaterThanOrEqual(self.value)
        )


class MustHaveLengthLessThan(Validator):
    """Validates that the iterable has length less than the specified
    value.
    """

    def __init__(self, value: int):
        self.value = value

    def __call__(self, arg_value: Sized, arg_name: str):
        _iterable_len_validator(
            arg_value, arg_name, func=MustBeLessThan(self.value)
        )


class MustHaveLengthLessThanOrEqual(Validator):
    """Validates that the iterable has length less than or equal to
    the specified value.
    """

    def __init__(self, value: int):
        self.value = value

    def __call__(self, arg_value: Sized, arg_name: str):
        _iterable_len_validator(
            arg_value, arg_name, func=MustBeLessThanOrEqual(self.value)
        )


class MustHaveLengthBetween(Validator):
    """Validates that the iterable has length between the specified
    min_value and max_value.
    """

    def __init__(
        self,
        *,
        min_value: int,
        max_value: int,
        min_inclusive: bool = True,
        max_inclusive: bool = True,
    ):
        """
        :param min_value: The minimum value (inclusive or exclusive based
                          on min_inclusive).
        :param max_value: The maximum value (inclusive or exclusive based
                          on max_inclusive).
        :param min_inclusive: If True, min_value is inclusive.
        :param max_inclusive: If True, max_value is inclusive.
        """
        self.func = MustBeBetween(
            min_value=min_value,
            max_value=max_value,
            min_inclusive=min_inclusive,
            max_inclusive=max_inclusive,
        )

    def __call__(self, arg_value: Sized, arg_name: str):
        _iterable_len_validator(arg_value, arg_name, func=self.func)


class MustHaveValuesGreaterThan(Validator):
    """Validates that all values in the iterable are greater than the
    specified min_value.
    """

    def __init__(self, min_value: Number):
        self.min_value = min_value

    def __call__(self, values: Iterable, arg_name: str):
        _iterable_values_validator(
            values, arg_name, func=MustBeGreaterThan(self.min_value)
        )


class MustHaveValuesGreaterThanOrEqual(Validator):
    """Validates that all values in the iterable are greater than or
    equal to the specified min_value.
    """

    def __init__(self, min_value: Number):
        self.min_value = min_value

    def __call__(self, values: Iterable, arg_name: str):
        _iterable_values_validator(
            values, arg_name, func=MustBeGreaterThanOrEqual(self.min_value)
        )


class MustHaveValuesLessThan(Validator):
    """Validates that all values in the iterable are less than the
    specified max_value.
    """

    def __init__(self, max_value: Number):
        self.max_value = max_value

    def __call__(self, values: Iterable, arg_name: str):
        _iterable_values_validator(
            values, arg_name, func=MustBeLessThan(self.max_value)
        )


class MustHaveValuesLessThanOrEqual(Validator):
    """Validates that all values in the iterable are less than or
    equal to the specified max_value.
    """

    def __init__(self, max_value: Number):
        self.max_value = max_value

    def __call__(self, values: Iterable, arg_name: str):
        _iterable_values_validator(
            values, arg_name, func=MustBeLessThanOrEqual(self.max_value)
        )


class MustHaveValuesBetween(Validator):
    """Validates that all values in the iterable are between the
    specified min_value and max_value.
    """

    def __init__(
        self,
        *,
        min_value: Number,
        max_value: Number,
        min_inclusive: bool = True,
        max_inclusive: bool = True,
    ):
        """
        :param min_value: The minimum value (inclusive or exclusive based
                          on min_inclusive).
        :param max_value: The maximum value (inclusive or exclusive based
                           on max_inclusive).
        :param min_inclusive: If True, min_value is inclusive.
        :param max_inclusive: If True, max_value is inclusive.
        """
        self.func = MustBeBetween(
            min_value=min_value,
            max_value=max_value,
            min_inclusive=min_inclusive,
            max_inclusive=max_inclusive,
        )

    def __call__(self, values: Iterable, arg_name: str):
        _iterable_values_validator(values, arg_name, func=self.func)
