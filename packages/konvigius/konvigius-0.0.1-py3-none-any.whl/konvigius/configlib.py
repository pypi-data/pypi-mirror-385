# src/konvigius/configlib.py
"""
"""
from __future__ import annotations
from collections import defaultdict
from collections.abc import Sized
from dataclasses import dataclass, field, InitVar
import json
from types import SimpleNamespace
from typing import Any

from .exceptions import (ConfigError, ConfigMetadataError, ConfigValidationError,
                         ConfigRangeError, ConfigDomainError, ConfigTypeError,
                         ConfigRequiredError, ConfigInvalidFieldError)

from .validators import (RequiredValidator, TypeValidator, RangeValidator, 
                         DomainValidator, CustomValidator, ComputedValidator)

# ----------------------------------------------------------------------------- 
# 0. Define the Schema metadata class
# ----------------------------------------------------------------------------- 

@dataclass(kw_only=True)
class Schema:
    """
    """
    name: str = field(kw_only=False)
    short_flag: str | None = None
    field_type: type | None = None
    default: Any | None = None
    required: bool | None = None
    r_min: int | None = None
    r_max: int | None = None
    domain: set[Any] | None = None
    fn_validator: Callable | tuple(Callable) | None = None
    fn_computed: Callable | tuple(Callable) | None = None
    help_text: str | None = None
    no_validate: bool  = False 

# ----------------------------------------------------------------------------- 
# 1. Define the Option metadata class
# ----------------------------------------------------------------------------- 

class Option:
    def __init__(self, entry: Schema, help_map: dict[str, str] = None):
        self.default_value: Any | None = entry.default
        self.name, self.short_flag = Option.parse_entryname(entry.name, entry.short_flag)
        self.field_type: type | None = entry.field_type
        self.required: bool | None = entry.required 
        self.r_min: int = entry.r_min
        self.r_max: int = entry.r_max
        self.domain: set[Any] | None = entry.domain
        self.fn_validator: callable | None = entry.fn_validator
        self.fn_computed: callable | None = entry.fn_computed
        self.do_validate: bool | None = not entry.no_validate
        self.help_text: str | None = (entry.help_text if entry.help_text 
                                          else f"Help: {self.name} "
                                               f"(default {self.default_value})")
        if help_map:
            self.help_text: str = help_map.get(self.name, entry.help_text)

    @staticmethod
    def parse_entryname(ename: str, short_flag: str):
        """
        Indien short_flag expliciet is opgegeven, dan heeft deze voorrang.
        """
        name, sep, _short_flag = ename.partition("|")
        _short_flag = short_flag or _short_flag
        if not name:
            raise ConfigMetadataError(f"Schema name not valid ({ename})")
        if _short_flag and len(_short_flag) != 1:
            raise ConfigMetadataError(f"short CLI flags must be a single "
                                      f"character: '{_short_flag}'")
        return name, _short_flag or None

    # At Option level the validation can be switched on/off (a Schema option)

    def init_validators(self):
        self._validators = [] 
        if self.do_validate:   # at Option level validation can be switched on/off
            self._validators.append(TypeValidator(self))
            self._validators.append(RequiredValidator(self))
            self._validators.append(DomainValidator(self))
            self._validators.append(RangeValidator(self))
            # custom and computes validators:
            self._custom_validator = CustomValidator(self)
            self._comp_validator = ComputedValidator(self)

    def validate_default(self, value: Any, cfg: Config):
        if self.do_validate:   
            for validator in self._validators:
                validator(value,cfg=cfg.copy_config(dirty=True)) 

    def validate_custom(self, value: Any, cfg: Config):
        if self.do_validate:   # at Option level validation can be switched on/off
            self._custom_validator(value, cfg=cfg.copy_config(dirty=True))

    def validate_computed(self, value: Any, cfg: Config):
        if self.do_validate:   # at Option level validation can be switched on/off
            values_computed = self._comp_validator(value, cfg=cfg.copy_config(dirty=True))
            for fname, value in values_computed.items():
                cfg._computed_values[fname] =value

    def __repr__(self):
        return f"<Config: name={self.name!r}, field_type={self.field_type!r}, "\
               f"default_value={self.default_value!r} ...>"

    def __str__(self):
        header = "<Option values>"
        #body = [f"  {name}: {getattr(self, name)!r}" for name, alue in vars(self)]
        body = [f"  - {name}: {value!r}" for name, value in vars(self).items() if not name.startswith('_')]
        lines = [header] + body
        return "\n".join(lines)

# ----------------------------------------------------------------------------- 
# 2. Define the descriptor to handle access + validation
# ----------------------------------------------------------------------------- 

class ConfigField:
    """
    Descriptor that manages access and validation for a single config field.

    Each ConfigField wraps a `ConfigOption`, which defines the metadata
    (e.g., default value, type constraints, min/max range) for that field.

    This descriptor is installed on dynamically generated `Config` subclasses
    via the `config_factory()` method. It intercepts attribute access to:

    - Return either the set value or the default.
    - Validate assigned values before storing.
    """    
    # def __init__(self, option: Option):
    def __init__(self, option: Option):
        """
        Initializes the descriptor with the associated ConfigOption.

        Args:
            option (Option): Metadata describing the field
                             (default, type, constraints, etc.)
        """        
        self.option = option

    def __get__(self, cfg, owner):
        """
        Retrieves the value of the config field for the given instance (cfg).

        - If accessed via the class (e.g., `ConfigClass.field`), returns the descriptor itself.
        - If accessed via an instance, returns the stored value or the default.

        Args:
            instance (Config): The config instance this field belongs to.
            owner (type): The owner class.

        Returns:
            Any: The current value of the field, or its default if unset.
        """ 
        if cfg is None:
            return self  # Accessed from class
        return cfg._pending_values.get(self.option.name, cfg._values[self.option.name])

        #return cfg._values.get(self.name, self.option.default_value)

    def __set__(self, cfg, value):
        """
        Validates and sets the value of the config field on the given instance (cfg).

        This method ensures the assigned value meets all constraints defined in
        the associated `ConfigOption`, such as type, min, and max.

        Args:
            instance (Config): The config instance this field belongs to.
            value (Any): The value to be assigned.

        Raises:
            A ConfigError: If the value fails validation.
        """
        #print("* Config_Field:", self.option.name, " old", cfg._values[self.option.name], " new:", value, " _trx_", cfg._trx_)
        if cfg._trx_:
            # transaction mode, put all in pending datastore
            cfg._pending_values[self.option.name] = value
        else:
            self.option.validate_default(value, cfg)
            self.option.validate_custom(value, cfg)
            cfg._values[self.option.name] = value
            self.option.validate_computed(value, cfg)

# ----------------------------------------------------------------------------- 
# 3. Config class that manages instance state and metadata
# ----------------------------------------------------------------------------- 

class Config:
    """
    Base class for dynamically generated configuration objects.

    This class is not used directly, but acts as a base for subclasses
    created by `Config.config_factory()` or `Config.from_dict()`.

    Each instance manages:
    - `_values`: The actual runtime values for each config field.
    - `_metadata`: A dictionary of ConfigOption objects keyed by field name,
                   used for validation, default handling, and introspection.
    """
    def __init__(self):
        """
        Initializes internal state for a Config instance.

        - `_values` holds actual values set by the user or defaults.
        - `_metadata` holds the schema (ConfigOption) for each config field.

        Normally this constructor is called indirectly via `config_factory()`.
        """        
        self._values = {}                     # current values per instance
        self._pending_values = {}             # mutated values per instance
        self._computed_values = {}            # derived values per instance
        self._metadata = {}                   # Option objects per field
        self._trx_: bool = False              # transaction mode  

    def _create_inverted_bool_properties(self):
        """
        Lazy operation.
        """
        # helper function returning a closure:
        def fn_return_inverted(source_field: str, field_name: str):
            def fn_return_bool(value: str, cfg: Config) -> bool:
                value = cfg._values[source_field] 
                return not value
            fn_return_bool.field_name = field_name
            return fn_return_bool

        for option in self._metadata.values():

            if not option.do_validate:
                continue

            existing = list(option._comp_validator.compute_callbacks)
            if option.field_type is bool:
                if option.name.startswith("no_"):
                    field_name = option.name.partition('_')[2]
                else:
                    field_name = 'no_' + option.name

                if field_name and field_name not in self._metadata:
                    existing.append(fn_return_inverted(option.name, field_name))
            option._comp_validator.compute_callbacks = tuple(existing)

    def _create_computed_properties(self):
        """
        This will create the read-only properties for the config-instance based on the
        metadata object ConfigOption.computed.
        These properties return their values from cfg._computed_values.
        """
        cfg = self
        for option in self._metadata.values():

            if not option.do_validate:
                continue

            for fn in option._comp_validator.compute_callbacks:
                if fn.field_name in self._metadata:
                    # the computed fieldname may not be already in use
                    raise ConfigInvalidFieldError(
                               "cannot create computed field "
                               f"'{fn.field_name}', field already exists; "
                               "choose a different name.", 
                               fn.field_name)

                # create a property (wihtout setter) for this computed field
                prop = property(make_getter(fn.field_name))
                setattr(cfg.__class__, fn.field_name, prop) 

    def start_transaction(self):
        if self._trx_:
            return

        self._trx_ = True
        self._pending_values.clear()

    def commit_transaction(self):
        if not self._trx_:
            return

        merged = {**self._values, **self._pending_values} 

        try:
            # Run the validators
            for option in self._metadata.values():
                option.validate_default(merged[option.name], self)

            # Run the custom validators
            for option in self._metadata.values():
                option.validate_custom(merged[option.name], self)

            # Run the computes validators 
            for option in self._metadata.values():
                option.validate_computed(merged[option.name], self)

            # at this point no exception was raised, copy merged to the actual datastore (this is the commit phase)
            self._values = merged

        except Exception as e:
            raise ConfigError(f"Commit raised an error (changes are undone): {e}")

        finally:
            self._trx_ = False
            self._pending_values.clear()


    def rollback_transaction(self):
        self._trx_ = False
        self._pending_values.clear()

    @classmethod
    def config_factory(cls, schema: list[Schema], *,
                       help_map: dict[str, str] = None, cfg_validate: bool = True,
                       auto_bools: bool = True,
                       # values_sync: bool = False 
        ) -> Config:
        """
        Dynamically creates a Config subclass with fields based on the provided
        schema.

        This method constructs a subclass of Config by injecting `ConfigField` 
        descriptors for each field defined in the schema. Each field name may 
        include a short CLI flag (e.g., `"timeout|t"`), but only the long name
        is used as the attribute name on the config object.

        This is the core entry point for schema-based config creation.

        Args:
            options (dict[str, ConfigOption]): 
                A dict of (name, ConfigOption) pairs. The `name` may include 
                a pipe character to specify a short CLI flag 
                (e.g., `"username|u"`).

            help_map (dict[str, str], optional): 
                Mapping from long field names to help text. This will inject
                the helptext into the corresponding ConfigOption object.

            auto_bools (bool, optional):


            values_sync (bool, optional): 
                If True, default values are populated into _values at 
                instantiation. Use this when there is need for to have all 
                default values readily available. Default false.

        Returns:
            Config: An instance of a dynamically generated Config subclass.

        Raises:
            ConfigMetadataError: If any ConfigOption metadata is invalid or a 
                                 short flag is longer than 1 character.

        Example:
            schema = {
                "username|u" : ConfigOption(default_value="guest", 
                                            field_type=str)),
                "timeout|t" : ConfigOption(default_value=30, min=1, max=60, 
                                           field_type=int)),
            }
            cfg = Config.config_factory(schema)
            print(cfg.username)  # → 'guest'
        """

        # Create the ConfigField objects, each referencing an Option object.

        namespace = {}
        for entry in schema:
            option = Option(entry, help_map)
            namespace[option.name] = ConfigField(option)

        # Create a Config instance dynamically

        Config_cls = type('DynamicConfig', (cls,), namespace)
        cfg = Config_cls()

        # Instantiate the default validators and fill the backend datastore

        for config_field in namespace.values():
            option = config_field.option # aliasing
            option.init_validators()
            cfg._metadata[option.name] = option
            cfg._values[option.name] = option.default_value

        # Run the validators

        for option in cfg._metadata.values():
             option.validate_default(cfg._values[option.name], cfg)

        # Run the custom validators

        for option in cfg._metadata.values():
            option.validate_custom(cfg._values[option.name], cfg)

        # Add properties for bool typed ConfigOptions: inverted bools.

        if auto_bools:
            cfg._create_inverted_bool_properties()

        # Create properties for the conputed-functions from the Schema-field fn_computed

        cfg._create_computed_properties()

        # Run the field-computation validators

        for option in cfg._metadata.values():
            option.validate_computed(cfg._values[option.name], cfg)

        # if values_sync:
        #     for field_name, option in cfg._metadata.items():
        #         cfg._values[field_name] = option.default_value

        return cfg

    @classmethod
    def from_dict(cls, options: list[tuple[str, ConfigOption]], values: dict):
        """
        Creates a Config instance from a schema and a dictionary of override 
        values.

        Use this to load user-configured values in a dictionary while falling 
        back on defaults defined in the schema.

        This method:
        - Calls `config_factory()` to construct the config instance based on 
          schema
        - Applies override values from the provided dictionary
        - Performs validation on all overridden values

        Args:
            options (list): A list of (name, ConfigOption) pairs defining the 
            schema.
            values (dict): A dictionary of values to override defaults.

        Returns:
            Config: A fully validated config instance with applied overrides.

        Raises:
            ConfigInvalidFieldError: If a key in `values` is not part of the schema.
            ValueError / TypeError: If any override value fails validation.
        """
        cfg = cls.config_factory(options)

        for name, value in values.items():
            if name not in cfg._metadata:
                raise ConfigInvalidFieldError(
                        f"Invalid config field: '{name}'.",
                        name)

            setattr(cfg, name, value)  # triggers validation via descriptor

        return cfg

    def get_computed_prop(self, name):
        """
        Returns the value produced by the fn_computed attribute (callable) from 
        the metadata object (Option) for the given field name.

        Note:
        The value of 'name' can also be retrieved on the cfg instance as
        a regular fieldname: cfg.some_computed_field (a property).

        Args:
            name (str): The name of the field with the derived value.

        Returns:
            Some value (Any): The values that was produced.
        """
        return self._computed_values.get(name, f"Field '{name}' is invalid")


    def get_meta(self, name):
        """
        Returns the ConfigOption metadata object for the given field name.

        This can be used for introspection, e.g., to inspect default values,
        type expectations, or constraints.

        Args:
            name (str): The name of the config field.

        Returns:
            ConfigOption or None: The metadata object for the field, or None
            if the field is not defined in this config instance.
        """
        return self._metadata.get(name)


    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the current config values.

        This includes both default values and any values overridden at runtime.

        Returns:
            dict: A mapping of field names to their current values.
        """
        #TODO: is deze methode nodig in deze vorm ?
        return {
            name: getattr(self, name)
            for name in self._metadata.keys()
        }

    def to_json(self, *, indent: int = 2) -> str:
        """
        Serializes the current config values to a JSON-formatted string.

        Args:
            indent (int): Number of spaces for indentation in the JSON output.

        Returns:
            str: JSON string of the current config values.
        """
        #TODO: is deze methode nodig in deze vorm ?
        return json.dumps(self.to_dict(), indent=indent)

    def info_vars(self, chop_at: int = 40) -> str:
        """
        Utility to display field names, values and their help text from the 
        config object.

        The table is formatted as markdown.

        Args:
            chop_at (int): Maximum length of the fields (default 40)

        Returns:
            str: a string with the markdown table.
        """
        chop_at = chop_at if chop_at > 15 else 15
        # create table header
        lengths = [str(ln) if ln < chop_at else chop_at for ln in (15, 22, 6, 40)]
        headers = zip(['Field', 'Value', 'Source', 'Description'], lengths)
        lines = ['| ' +  ' | '.join([ f'{h[0]:<{h[1]}}' for h in headers]) + ' |']
        headers = zip(list('----'), lengths)
        lines.append('| ' +  ' | '.join([ f'{h[0]*int(h[1])}' for h in headers]) + ' |')

        sorted_rows = sorted(self)

        for row in sorted_rows:
            if (name := row[0]) in self._metadata:
                desc = self._metadata[name].help_text or ""
            else:
                desc = "Field: " + name
            zrow = zip(row + (desc,), lengths)
            lines.append("| " + " | ".join(f"{cell[0]!r:<{cell[1]}}" for cell in zrow) + " |")

        return "\n".join(lines)

    def copy_config(self, dirty=False) -> SimpleNameSpace:
        """Create a simple copy of the config attribute values."""
        data = {fname: value for fname, value, _ in self}
        data['_values'] = {**self._values}
        data['_computed_values'] = {**self._computed_values}
        if dirty:
            data = {**data, **self._pending_values}

        return SimpleNamespace(**data)

    # ALTERNATIVE VERSION in case the current version will no do anymore some day
    #
    # def copy_config(self):
    #     from dataclasses import make_dataclass
    #     fields = [(fname, type(value)) for fname, value, _ in self]
    #     CopiedConfig = make_dataclass("CopiedConfig", fields)
    #     values = {fname: value for fname, value, _ in self}
    #     return CopiedConfig(**values)

    def __len__(self):
        """
        Return number of config_fields + generated properties like computed fields and
        auto generated inverted booleans.
        """
        return len(self._values) + len(self._computed_values)

    def __iter__(self):
        yield from ((key, value, 'S') for key, value in self._values.items()) 
        yield from ((key, value, 'C') for key, value in self._computed_values.items()) 

    def __str__(self):
        header = "<Config values>"
        body = [f"  {name}: {getattr(self, name)!r}" for name in self._metadata]
        lines = [header] + body
        return "\n".join(lines)

    def __repr__(self):
        items = [f"{k}={getattr(self, k)!r}" for k in self._metadata]
        joined = ", ".join(items)
        return f"<Config: {joined}>"

    @staticmethod
    def get_manual():
        """Returns the manual text of the validconf package."""
        return __doc__


# === Module functions ===

def make_getter(attr):
    def getter(self):
        return self._computed_values[attr]
    return getter

# this function will not be used/called in this package
# it is there for documentation purposes only
def make_setter(attr):
    def setter(self, value):
        self._computed_values[attr] = value
    return setter

def with_field_name(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        fn.field_name = name  # type: ignore[attr-defined]
        return fn
    return decorator


# === END ===
