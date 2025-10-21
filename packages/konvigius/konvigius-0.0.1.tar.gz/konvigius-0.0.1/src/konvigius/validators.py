# src/konvigius/validators.py
"""
validators.py

This module provides a set of configurable and reusable validator classes
designed to validate configuration or user-provided data by means of Schema object(s).

All validators inherit from a common abstract base class, `Validator`, which enforces
implementation of a `_init_validate()` method and a `_validate_value` method.

Each validator-class is designed to check a specific constraint (e.g., type,
range, presence, or membership in a domain), and raise a validation exception if the 
constraint is not met.

These validators are created automatically when instantiating a Config class.

Classes:
    Validator (ABC): Abstract base class for all validators. Implements a callable
        interface that delegates to the subclass's methods.

    TypeValidator: Validates that a value is of a specified type or set of types.

    RequiredValidator: Validates that a value is present (i.e., not None or empty string)
        if it is marked as required.

    RangeValidator: Validates that a numeric value falls within a specified inclusive
        range defined by `min_val` and `max_val`.

    DomainValidator: Validates that a value exists within a predefined set of allowed values.

    CustomValidator: Validates a value using a user-provided function(s). This allows
        for flexible or domain-specific validation logic. Unexpected errors are
        wrapped in a `ConfigValidationError`, while known config exceptions are re-raised.

    ComputedValidator: Validates user-provided function(s) and creates new properties
    that are added to the config-instance.

Note:
    All validators are dataclasses for convenient instantiation and introspection.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable
from .exceptions import (ConfigError, ConfigMetadataError, ConfigValidationError,
                         ConfigRangeError, ConfigDomainError, ConfigTypeError,
                         ConfigRequiredError)


@dataclass
class Validator(ABC):
    """
    The Validator class is the base class for subclasses that perform checks on a value.

    When instantiating all subclasses, the `__init__` parameters are validated.
    If these checks fail, a ConfigError is raised.

    Each subclass must implement the `_init_validate` and `_validate_value` methods.
    """
    option: "Option"

    def __post_init__(self):

        result = self._validator(self._init_validate)


    def __call__(self, value: Any, cfg: "Config" ):
        self.cfg = cfg
        result = self._validator(self._validate_value, value=value)

        return result

    def _validator(self, fn: Callable, **kwargs):

        try:
            result = fn(**kwargs)
        except Exception as e:
            if isinstance(e, ConfigError):
                # Re-raise with amended message, preserving subclass
                new_exc = type(e)(f"{self.__class__.__name__}: {e}")
                raise new_exc from e
            else:
                # Wrap all other exceptions in ConfigValidationError
                raise ConfigValidationError(f"{self.__class__.__name__} [{type(e).__name__}]: {e}") from e

        return result

    @abstractmethod
    def _init_validate(self, **kwargs):
        pass

    @abstractmethod
    def _validate_value(self, value: Any) -> None | dict[str, Any]:
        """
        Validate the given value.

        Args:
            value (Any): The value to validate.

        Returns:
            None | dict[str, Any]: Depending on the subclass.

        Raises:
            Any validation-specific exception (e.g., ConfigValidationError).
        """
        pass


@dataclass
class TypeValidator(Validator):
    """
    Validates whether a given value is of the specified data type(s).
    """
    def _init_validate(self):
        """
        Validates that `field_type` is a type or tuple of types.
        
        Raises:
            ConfigTypeError: If `field_type` contains non-type elements.
        """
        self._type = self.option.field_type  # make short alias
        if self._type is not None:
            if not isinstance(self._type, tuple):
                    self._type = tuple([self._type])

            for ft in self._type: 
                if not isinstance(ft, type):
                    raise ConfigTypeError(
                          f"'field_type' must be a class type like str, int, bool etc; "
                          f"got type {type(ft).__name__}")

    def _validate_value(self, value: Any):
        """
        Validates whether the given `value` is of the allowed type(s).

        Args:
            value (Any): The value to validate.

        Raises:
            ConfigTypeError: If the value is not of the expected type.
        """
        if self._type is not None:
            if value and not isinstance(value, self._type):
                raise ConfigTypeError(
                       "value is of the wrong type; "
                      f"got type {type(value).__name__}")


@dataclass
class RequiredValidator(Validator):
    """
    Validates that a required value is not None or an empty string.

    This validator checks whether a value is present (i.e., not None and not an empty string)
    if the `required` flag is set to True.
    """

    def _init_validate(self):
        """
        Post-initialization hook to ensure `required` is a valid boolean.

        If `required` is None or an empty string, it is treated as False.

        Raises:
            ConfigTypeError: If `required` is not of type bool.
        """
        if self.option.required in (None, ''):
            self.option.required = False
        if not isinstance(self.option.required, bool):
            raise ConfigTypeError("'required' must be of type boolean; "
                                  f"got value '{self.option.required}'"
            )

    def _validate_value(self, value: Any):
        """
        Validates that the value is not None or an empty string when required.

        Args:
            value (Any): The value to validate.

        Raises:
            ConfigRequiredError: If the value is None or empty and `required` is True.
        """
        if self.option.required and (value is None or value == ''):
            raise ConfigRequiredError("value can not be None or empty")


@dataclass
class RangeValidator(Validator):
    """
    Validates that a numeric value falls within a specified range.

    This validator checks whether a value (int or float) lies between
    `min_val` and `max_val`, inclusive. If either bound is not set (None),
    that side of the range is considered open.
    """
    def _init_validate(self):
        """
        Validates and normalizes the min_val and max_val bounds after initialization.
        """
        if self.option.r_min is not None and not isinstance(self.option.r_min, (float, int)):
            raise ConfigTypeError(
                      f"value min_val must be int or float; "
                      f"got type {type(self.option.r_min).__name__}",
            )
        if self.option.r_max is not None and not isinstance(self.option.r_max, (float, int)):
            raise ConfigTypeError(
                      f"value max_val must be int or float; "
                      f"got type {type(self.option.r_max).__name__}",
            )
        if self.option.r_min is not None and self.option.r_max is not None and self.option.r_min > self.option.r_max:
            raise ConfigRangeError(
                      f"min ({self.option.r_min}) cannot be greater "
                      f"than max ({self.option.r_max})",
            )

    def _validate_value(self, value: int | float | str | None):
        """
        Validates that the value is within the defined numeric range.

        Empty strings and None are considered valid and skipped.

        Args:
            value (int | float | str | None): The value to validate.
                If a string, it is converted to None if empty.

        Raises:
            ConfigValidationError: If the value is not numeric,
                or if it falls outside the defined range.
        """
        if self.option.r_min is None and self.option.r_max is None:
            # testing makes no sense
            return

        value = None if value == '' else value
        if value is None:
            return

        if not isinstance(value, (float, int)):
            value = len(value)

        if self.option.r_min is not None and value < self.option.r_min:
            raise ConfigRangeError(
                  f"value ({value}) must be >= min-value ({self.option.r_min})",
            )
        if self.option.r_max is not None and value > self.option.r_max:
            raise ConfigRangeError(
                  f"value ({value}) must be <= max-value ({self.option.r_max})",
            )


@dataclass
class DomainValidator(Validator):
    """
    Validates that a value exists within a predefined domain (set of acceptable values).

    This validator ensures the value is present in the `domain` set.
    The domain must be a non-empty set, provided at initialization.
    """
    def _init_validate(self):
        """
        Validates that `domain` is a non-empty set after initialization.

        Raises:
            ConfigMetadataError: If `domain` is not a set or is empty.
        """
        if ((self.option.domain is not None) and (self.option.domain == set() 
            or not isinstance(self.option.domain, set))):
            raise ConfigTypeError(
                  f"domain must be a set() collection (not empty); "
                  f"got type {type(self.option.domain).__name__}",
            )

    def _validate_value(self, value: Any) -> bool:
        """
        Validates that the given value is part of the domain set.

        Args:
            value (Any): The value to validate.

        Raises:
            ConfigDomainError: If the value is not in the domain set.
        """
        if self.option.domain and value not in self.option.domain:
            raise ConfigDomainError(
                  f"value ({value}) is not in the domain of acceptable values",
            )

@dataclass
class CustomValidator(Validator):
    """
    A validator that delegates validation logic to a user-defined function.

    This class allows dynamic or reusable validation logic by accepting
    a custom function (`fn_validator`) at initialization. The function should
    raise a `ConfigError` or another appropriate exception if validation fails.

    Attributes:
        fn_validator (Callable[[Any], Any]): A user-provided function that performs
            validation. It should accept a single argument (the value to validate)
            and either return a result or raise an exception.
    """
    # fn_validator: Callable[[Any], Any] = None

    def _init_validate(self):
        """
        Validates that `fn_validators` is a type or tuple of types.
        
        Raises:
            ConfigTypeError: If `fn_validator` contains non-function elements.
        """
        if self.option.fn_validator is None:
            self.option.fn_validator = tuple()

        # if self.option.fn_validator is not None:
        if not isinstance(self.option.fn_validator, tuple):
            self.option.fn_validator = tuple([self.option.fn_validator])

        for fn in self.option.fn_validator: 
            if not isinstance(fn, Callable):
                raise ConfigTypeError(
                      f"custom validators must be a callable or a tuple of callables; "
                      f"got type {type(fn).__name__}")


    def _validate_value(self, value: Any) -> bool:
        """
        Executes the user-defined validation function with the provided value.

        Args:
            value (Any): The value to validate.

        Raises:
            ConfigError: If the user-defined function raises this known validation exception.
            ConfigValidationError: If an unexpected exception occurs during validation.
        """
        # if self.option.fn_validator is None:
        #     return

        for fn in self.option.fn_validator:
            fn(value, self.cfg)


@dataclass
class ComputedValidator(Validator):
    """
    """
    def _init_validate(self):
        """
        Validates that `fn_validators` is a type or tuple of types.
        
        Raises:
            ConfigMetadataError: If `fn_validator` contains non-function elements.
        """
        if self.option.fn_computed is None:
            self.option.fn_computed = tuple()

        self.compute_callbacks = self.option.fn_computed
        if self.compute_callbacks is None:
            self.compute_callbacks = tuple()
        else:
            if not isinstance(self.compute_callbacks, tuple):
                self.compute_callbacks = tuple([self.compute_callbacks])

            for fn in self.compute_callbacks: 
                if not isinstance(fn, Callable):
                    raise ConfigTypeError(
                          f"computed (decorators) must be a callable or a tuple of callables; "
                          f"got type {type(fn).__name__}")


    def _validate_value(self, value: Any) -> dict[str, Any]:
        """
        Executes the user-defined function with the provided value.

        Args:
            value (Any): The value to validate.

        Returns:
            dict[str, Any]: The results of the user-defined validation functions, if successful.

        Raises:
            ConfigError: If the user-defined function raises this known validation exception.
            ConfigValidationError: If an unexpected exception occurs during validation.
        """
        fields = dict()
        for fn in self.compute_callbacks:
            fields[fn.field_name] = fn(value, self.cfg)

        return fields

# @dataclass
# class NumRange:
#     lo: int | float | None = None
#     hi: int | float | None = None
#
#     def contains(self, value: int | float) -> bool:
#         if self.lo is not None and value < self.lo:
#             return False
#         if self.hi is not None and value > self.hi:
#             return False
#         return True


# === END ===
