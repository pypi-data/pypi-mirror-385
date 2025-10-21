from typing import Any, Callable
import pytest
import json
"xyzab"
from konvigius.configlib import Config, Schema, Option, with_field_name
# from konvigius.computedfield import ComputedField
from konvigius.exceptions import (ConfigError, ConfigMetadataError, ConfigValidationError,
                                  ConfigRangeError, ConfigDomainError, ConfigTypeError,
                                  ConfigRequiredError, ConfigInvalidFieldError)

# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def schema():
    return [
       Schema("debug|d", default=False, field_type=bool),
       Schema("wrap", default=True, field_type=bool),
       Schema("no_welcome", default=True, field_type=bool),
       Schema("timeout|t", default=10, field_type=int, r_min=1, r_max=60),
       Schema("threshold", default=0.5, field_type=float),
       Schema("count", default=5, r_min=1, r_max=10, field_type=int),
       Schema("username", default="guest", field_type=str),
       Schema("even_number", default=2, field_type=int, ),
       Schema("x", default=1, field_type=int),
       Schema("y", default=2, field_type=int),
       Schema("z", default="abc", field_type=str),
       Schema("some_field", default="hello", field_type=str),
    ]

@pytest.fixture
def schema_derived_seconds():
    @with_field_name('time_in_seconds')
    def fn_seconds(value, cfg: Config):
        return cfg.time_in_minutes * 60

    return [
       Schema("time_in_minutes", default=2, field_type=int, fn_computed=fn_seconds,),
       Schema("some_field", default=0, field_type=int)
    ]

# -----------------------------------------------------------------------------

def test_simple_schema():
    schema = [
        Schema("username", default="guest", field_type=str),
    ]
    cfg = Config.config_factory(schema)



def test_basic_config_factory_and_access(schema):

    cfg = Config.config_factory(schema)
    
    assert cfg.debug is False
    assert cfg.timeout == 10
    assert cfg.to_dict() == {"debug": False, "timeout": 10, "threshold": 0.5,
                             "count":5, "username": "guest", "even_number":2,
                             "x":1, "y":2, "z":"abc", "some_field":"hello",
                             "wrap":True, "no_welcome":True}
    assert isinstance(cfg.to_json(), str)

def test_simple_validation():
    schema = [
        Schema("username", default="guest", field_type=str),
        Schema("debug", default=False, field_type=bool),
        Schema("no_wrap", default=True, field_type=bool),
        Schema("timeout", default=30, r_min=1, r_max=120, field_type=int),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.username == "guest"
    assert cfg.debug is False
    # assert cfg.no_debug is True
    # assert cfg.wrap is False
    assert cfg.no_wrap is True
    assert cfg.timeout == 30

def test_simple_range_validation():
    schema = [
        Schema("timeout", default=30, r_min=1, r_max=120, field_type=int),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.timeout == 30
    cfg.timeout = 1
    assert cfg.timeout == 1
    cfg.timeout = 120
    assert cfg.timeout == 120

def test_simple_range_validation_no_min_boundery():
    schema = [
        Schema("timeout", default=30, r_max=120, field_type=int),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.timeout == 30
    cfg.timeout = 1
    assert cfg.timeout == 1
    cfg.timeout = 120
    assert cfg.timeout == 120
    cfg.timeout = -1000
    assert cfg.timeout == -1000

def test_simple_range_validation_no_max_boundery():
    schema = [
        Schema("timeout", default=30, r_min=1, field_type=int),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.timeout == 30
    cfg.timeout = 1000
    assert cfg.timeout == 1000


def test_faulty_validator_init_type():
    schema = [
        Schema("timeout", default="twee", r_min=1, field_type=int),
    ]
    with pytest.raises(ConfigTypeError):
        cfg = Config.config_factory(schema)

def test_faulty_validator_init_required_1():
    schema = [
        Schema("timeout", r_min=1, field_type=int, required=True),
    ]
    with pytest.raises(ConfigRequiredError):
        cfg = Config.config_factory(schema)

def test_validator_init_required_False():
    schema = [
        Schema("timeout", r_min=1, field_type=int, required=False),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.timeout is None

def test_faulty_type_init_range_min():
    schema = [
        Schema("timeout", r_min="seven", field_type=int, required=True),
    ]
    with pytest.raises(ConfigTypeError):
        cfg = Config.config_factory(schema)

def test_faulty_type_init_range_max():
    schema = [
        Schema("timeout", r_max="eight", field_type=int, required=True),
    ]
    with pytest.raises(ConfigTypeError):
        cfg = Config.config_factory(schema)

def test_faulty_type_init_range_min_gt_max():
    schema = [
        Schema("timeout", r_min=50, r_max=5, field_type=int, required=True),
    ]
    with pytest.raises(ConfigRangeError):
        cfg = Config.config_factory(schema)

def test_range_no_max_raises():
    schema = [
        Schema("timeout", default=30, r_min=1, field_type=int),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.timeout == 30
    with pytest.raises(ConfigRangeError):
    # with pytest.raises(ConfigTypeError):
        cfg.timeout = 0

def test_range_no_min_raises():
    schema = [
        Schema("timeout", default=30, r_max=120, field_type=int),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.timeout == 30
    with pytest.raises(ConfigRangeError):
        cfg.timeout = 1000

def test_simple_range_validation_1():
    schema = [
        Schema("username", default="guest", field_type=str),
        Schema("debug", default=False, field_type=bool),
        Schema("no_wrap", default=True, field_type=bool),
        Schema("timeout", default=30, r_min=1, r_max=120, field_type=int),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.username == "guest"
    assert cfg.debug is False
    assert cfg.no_debug is True
    assert cfg.wrap is False
    assert cfg.no_wrap is True
    assert cfg.timeout == 30

def test_type_validation(schema):
    cfg = Config.config_factory(schema)
    with pytest.raises(ConfigTypeError):
        cfg.threshold = "not-a-float"


def test_range_validation(schema):
    cfg = Config.config_factory(schema)

    cfg.count = 6  # within range
    with pytest.raises(ConfigRangeError):
        cfg.count = 0  # below min
    with pytest.raises(ConfigRangeError):
        cfg.count = 20  # above max


def test_length_validation_on_str(schema):
    schema = [
       Schema("username", default="guest", field_type=str, r_min=3, r_max=10),
    ]
    cfg = Config.config_factory(schema)
    with pytest.raises(ConfigRangeError):
         cfg.username = "ab"
    with pytest.raises(ConfigRangeError):
        cfg.username = "a" * 11

#---1


def test_custom_validator_non_callable_raises():

    schema = [Schema("even_number", default=2, field_type=int,
                           fn_validator="functie-X")]
    with pytest.raises(ConfigTypeError):
        cfg = Config.config_factory(schema)

def test_custom_validator_multiple_non_callable_raises():

    schema = [Schema("even_number", default=2, field_type=int, 
                           fn_validator=( [1,2,3], "functie-X", 123,) )]
    with pytest.raises(ConfigTypeError):
        cfg = Config.config_factory(schema)

def test_custom_validator_ValidationError_raises():

    def must_be_even(value, cfg):
        if value % 2 != 0:
            raise ConfigValidationError("Value must be even")

    schema = [Schema("even_number", default=2, field_type=int, fn_validator=must_be_even)]
    cfg = Config.config_factory(schema)
    cfg.even_number = 4
    with pytest.raises(ConfigValidationError):
        cfg.even_number = 3

def test_custom_validator_ValueError_raises():

    def must_be_even(value, cfg):
        if value % 2 != 0:
            raise ValueError("Value must be even")

    schema = [Schema("even_number", default=2, field_type=int, fn_validator=must_be_even)]
    cfg = Config.config_factory(schema)
    cfg.even_number = 4
    with pytest.raises(ConfigValidationError):
        cfg.even_number = 3

def test_from_dict_with_unknown_key(schema):
    with pytest.raises(ConfigInvalidFieldError):
        Config.from_dict(schema, {"not_defined": 10})

def test_metadata_validation_errors():
    # min > max
    with pytest.raises(ConfigRangeError):
        Config.config_factory([
           Schema("invalid_field", default=1, r_min=10, r_max=5, field_type=int)
        ])

    # min < 0
    with pytest.raises(ConfigRangeError):
        Config.config_factory([
           Schema("negative_min", default=-2, r_min=-1, field_type=int)
        ])

def test_config_str_and_repr(schema):
    cfg = Config.config_factory(schema)

    assert "username: 'guest'" in str(cfg)
    assert "username='guest'" in repr(cfg)


def test_config_field_descriptor_behavior(schema):
    cfg = Config.config_factory(schema)
    assert cfg.some_field == "hello"
    cfg.some_field = "world"
    assert cfg.some_field == "world"

def test_help_map_injection(schema):
    help_map = {
        "timeout": "Timeout in seconds"
    }

    cfg = Config.config_factory(schema, help_map=help_map)
    assert cfg.timeout == 10 
    assert cfg.get_meta("timeout").help_text == "Timeout in seconds"

# === computes ===

def test_computed_field_NoneType():
    "OK: fn_compute == None"
    schema = [
        Schema("some_field", default="a test", field_type=str, fn_computed=None),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.some_field == "a test"
    assert cfg._metadata['some_field']._comp_validator.compute_callbacks == tuple()

@pytest.mark.parametrize("bad_type", [ "zanzibar", ("aa", "bb"), ["cc", "dd"], 123, 3.14])
def test_computed_field_wrong_type_raises(bad_type):

    schema = [
        Schema("some_field", default="a test", field_type=str, fn_computed=bad_type),
    ]
    with pytest.raises(ConfigTypeError):
        cfg = Config.config_factory(schema)

def test_computed_field_naming_conflict_raises():

    @with_field_name(name="great_car")
    def fn_tester(value: str, cfg: Config) -> Any:
        return value

    schema = [
        Schema("great_car", default="Porsche", field_type=str, fn_computed=fn_tester),
    ]
    with pytest.raises(ConfigInvalidFieldError):
        cfg = Config.config_factory(schema)

def test_computed_field_with_one_computed():

    @with_field_name(name="field_test_computed")
    def fn_tester(value: str, cfg: Config) -> Any:
        return value

    schema = [
        Schema("some_field", default="a test", field_type=str, fn_computed=fn_tester),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.some_field == "a test"

def test_computed_field_mutated_value():

    @with_field_name(name="f_computed")
    def fn_tester(value: str, cfg: Config) -> Any:
        return value.upper() + " (changed)"

    schema = [
        Schema("some_field", default="zanzibar", field_type=str, fn_computed=fn_tester),
    ]
    cfg = Config.config_factory(schema)
    assert cfg.some_field == "zanzibar"
    assert cfg.f_computed == "ZANZIBAR (changed)"

def test_computed_field_with_multiple_computed():

    @with_field_name(name="f_computed_1")
    def fn_tester_1(value: int, cfg: Config) -> Any:
        return value + 10

    @with_field_name(name="f_computed_2")
    def fn_tester_2(value: int, cfg: Config) -> Any:
        return value + 20

    @with_field_name(name="f_computed_3")
    def fn_tester_3(value: int, cfg: Config) -> Any:
        return value + 30

    schema = [
        Schema("some_field", default=1, field_type=int, 
                     fn_computed=(fn_tester_1, fn_tester_2, fn_tester_3))
    ]
    cfg = Config.config_factory(schema)
    assert cfg.some_field == 1
    assert cfg.f_computed_1 == 11
    assert cfg.f_computed_2 == 21
    assert cfg.f_computed_3 == 31
    cfg.some_field = 100
    assert cfg.some_field == 100
    assert cfg.f_computed_1 == 110
    assert cfg.f_computed_2 == 120
    assert cfg.f_computed_3 == 130

def test_computed_addition_via_cfg():

    @with_field_name(name="result_addition")
    def fn_calc_addition(value: int, cfg: Config) -> Any:
        return cfg.figure_A + cfg.figure_B + cfg.figure_C 

    schema = [
        Schema("figure_A", default=2, field_type=int, fn_computed=fn_calc_addition),
        Schema("figure_B", default=5, field_type=int, fn_computed=fn_calc_addition),
        Schema("figure_C", default=20, field_type=int, fn_computed=fn_calc_addition),
    ]

    cfg = Config.config_factory(schema)

    assert len(cfg) == 4

    assert cfg.figure_A == 2
    assert cfg.figure_B == 5
    assert cfg.figure_C == 20
    assert cfg.result_addition == 27

    cfg.figure_A = 100 

    assert cfg.figure_A == 100
    assert cfg.figure_B == 5 
    assert cfg.figure_C == 20
    assert cfg.result_addition == 125


def test_computed_bools():

    schema = [
        Schema("bool_A", default=True, field_type=bool),
        Schema("bool_B", default=False, field_type=bool),
    ]

    cfg = Config.config_factory(schema)

    assert len(cfg) == 4

    assert cfg.bool_A == True
    assert cfg.bool_B == False
    assert cfg.no_bool_A == False
    assert cfg.no_bool_B == True

    cfg.bool_B = True

    assert cfg.bool_A == True
    assert cfg.bool_B == True
    assert cfg.no_bool_A == False
    assert cfg.no_bool_B == False

    cfg.bool_A = False

    assert cfg.bool_A == False
    assert cfg.bool_B == True
    assert cfg.no_bool_A == True
    assert cfg.no_bool_B == False

def test_computed_bools_NO():

    schema = [
        Schema("bool_A", default=True, field_type=bool),
        Schema("bool_B", default=False, field_type=bool),
    ]

    cfg = Config.config_factory(schema, auto_bools=False) # auto_bools=Triu is default

    assert len(cfg) == 2

    assert cfg.bool_A == True
    assert cfg.bool_B == False

    cfg.bool_B = True

    assert cfg.bool_A == True
    assert cfg.bool_B == True

    cfg.bool_A = False

    assert cfg.bool_A == False
    assert cfg.bool_B == True

def test_computed_bools_modify_raises():

    schema = [
        Schema("bool_A", default=True, field_type=bool),
        Schema("bool_B", default=False, field_type=bool),
    ]

    cfg = Config.config_factory(schema)

    assert len(cfg) == 4

    with pytest.raises(AttributeError):
        cfg.no_bool_B = False

# -----------------------------------------------------------------------------
#  Test derived fields
# -----------------------------------------------------------------------------

def test_derived_minutes_to_seconds(schema_derived_seconds):

    cfg = Config.config_factory(schema_derived_seconds)
    assert cfg.time_in_minutes == 2
    assert cfg.get_computed_prop('time_in_seconds') == 2 * 60
    assert cfg.time_in_seconds == 2 * 60
    assert len(cfg) == 3


def test_derived_field_ending_spaces():

   @with_field_name('ending_spaces')
   def ending_spaces(value, cfg):
       return ' ' * cfg.num_spaces

   schema = [ Schema("num_spaces", default=3, field_type=int, fn_computed=ending_spaces),] 
   cfg = Config.config_factory(schema)
   assert cfg.ending_spaces == "   "  # 3 spaces


def test_derived_field_update_num_spaces():

   @with_field_name('ending_spaces')
   def ending_spaces(value, cfg):
       return ' ' * cfg.num_spaces

   schema = [ Schema("num_spaces", default=3, field_type=int, fn_computed=ending_spaces),] 
   cfg = Config.config_factory(schema)
   assert cfg.ending_spaces == "   "  # 3 spaces

   cfg.num_spaces = 5

   assert cfg.num_spaces == 5
   assert cfg.ending_spaces == "     "  # 5 spaces


def test_derived_field_exists_raises():

   @with_field_name('time_in_seconds')
   def calc_seconds(value, cfg):
       return cfg.time_in_minutes * 60

   schema = [Schema("time_in_minutes", default=3, field_type=int, fn_computed=calc_seconds),
             Schema("seconds", default=120, field_type=int),
   ]

   cfg = Config.config_factory(schema)
   assert cfg.time_in_minutes == 3
   assert cfg.time_in_seconds == 3 * 60



def test_derived_edit_property_raises(schema_derived_seconds):

    cfg = Config.config_factory(schema_derived_seconds)
    assert cfg.time_in_minutes == 2
    assert cfg.time_in_seconds == 2 * 60
    with pytest.raises(AttributeError, 
                       match="property 'getter' of 'DynamicConfig' object has "
                             "no setter"):
        cfg.time_in_seconds = 333

def test_derived_minutes_to_seconds_updated(schema_derived_seconds):

    cfg = Config.config_factory(schema_derived_seconds)
    assert cfg.time_in_minutes == 2
    assert cfg.time_in_seconds == 2 * 60
    cfg.time_in_minutes = 4
    assert cfg.time_in_seconds == 4 * 60

def test_userrole_port_mutation():

    def fn_check_port_admin(value, cfg):
        if value <= 1023 and cfg.userrole != 'admin':
            e = f"Port {value} not permitted; login as admin please." 
            raise ConfigValidationError(e)

    schema = [
        Schema("port|p", default=3274, r_min=0, r_max=65535, field_type=int, fn_validator=fn_check_port_admin ),
        Schema("userrole|r", default='guest', field_type=str),
    ]
    cfg = Config.config_factory(schema)

    assert cfg.userrole == 'guest'
    assert cfg.port == 3274
    cfg.start_transaction()
    cfg.port = 999              # mutating port to 999 before mutating userrole to admin will raise an exception
    cfg.userrole = 'admin'
    cfg.commit_transaction()
    assert cfg.userrole == 'admin'   
    assert cfg.port == 999 


def test__len__magic_function_1(schema):

    cfg = Config.config_factory(schema)
    assert len(cfg) == 15

def test_iter(schema):

    str_fields = """count:5:S
debug:False:S
even_number:2:S
no_debug:True:C
no_welcome:True:S
no_wrap:False:C
some_field:hello:S
threshold:0.5:S
timeout:10:S
username:guest:S
welcome:False:C
wrap:True:S
x:1:S
y:2:S
z:abc:S"""

    cfg = Config.config_factory(schema)
    assert len(cfg) == 15
    lines = []
    for name, value, source in cfg:
        lines.append(f"{name}:{value}:{source}")
    lines.sort()
    lines = '\n'.join(lines)
    assert lines == str_fields

def test_copy_config(schema):

    str_fields = """\
_computed_values:{'no_debug': True, 'no_wrap': False, 'welcome': False}
_values:{'debug': False, 'wrap': True, 'no_welcome': True, 'timeout': 10, 'threshold': 0.5, 'count': 5, 'username': 'guest', 'even_number': 2, 'x': 1, 'y': 2, 'z': 'abc', 'some_field': 'hello'}
count:5
debug:False
even_number:2
no_debug:True
no_welcome:True
no_wrap:False
some_field:hello
threshold:0.5
timeout:10
username:guest
welcome:False
wrap:True
x:1
y:2
z:abc"""

    cfg = Config.config_factory(schema)
    assert len(cfg) == 15
    lines = []
    cfg_copy = cfg.copy_config()
    cfg_dict = vars(cfg_copy)
    for name, value in cfg_dict.items():
        lines.append(f"{name}:{value}")
    lines.sort()
    lines = '\n'.join(lines)
    # print("\n:", str_fields, "\n:")
    # print("\n:", lines, "\n:")
    assert lines == str_fields
 #=== END ===
