# src/konvigius/exceptions.py

# === Config exceptions ===


class ConfigError(Exception):
    """
    Base class for all configuration-related errors.
    """

    def __init__(self, message: str, field: str = None, value: object = None):
        super().__init__(message)
        self.field = field
        self.value = value


class ConfigValidationError(ConfigError):
    """
    Raised when a config value fails validation.
    """

    def __init__(self, message: str, field: str = None, value: object = None):
        super().__init__(message, field, value)


class ConfigTypeError(ConfigValidationError):
    """
    Raised when a value is not of the expected type.
    """

    def __init__(
        self,
        message: str,
        field: str = None,
        field_type: type = None,
    ):
        super().__init__(message, field)
        self.field_type = field_type


class ConfigRequiredError(ConfigValidationError):
    """
    Raised when a value is not present.
    """

    def __init__(
        self,
        message: str,
        field: str = None,
    ):
        super().__init__(message, field)


class ConfigDomainError(ConfigValidationError):
    """
    Raised when a value is not present in a domain.
    """

    def __init__(
        self,
        message: str,
        field: str = None,
        value: object = None,
    ):
        super().__init__(message, field)


class ConfigRangeError(ConfigValidationError):
    """
    Raised when an integer/float is outside the defined min/max range.
    """

    def __init__(
        self,
        message: str,
        field: str = None,
        value: object = None,
        min_val: int = None,
        max_val: int = None,
    ):
        super().__init__(message, field)
        self.min_val = min_val
        self.max_val = max_val


class ConfigMetadataError(ConfigValidationError):
    """
    Raised when the schema metadata itself is invalid.
    """

    def __init__(self, message: str, field: str = None):
        super().__init__(message, field)


class ConfigComputedFieldError(ConfigMetadataError):
    """
    Raised when during creating a computed field.
    """

    def __init__(self, message: str, field: str = None):
        super().__init__(message, field)


class ConfigInvalidFieldError(ConfigError):
    """
    """
    def __init__(self, message: str, field: str = None):
        super().__init__(message, field)

# === END ===
