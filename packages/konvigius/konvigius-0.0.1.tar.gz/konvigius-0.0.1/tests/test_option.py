# tests/test_class_Option.py
import re
import pytest
from typing import Any
import types

from konvigius.configlib import Config, Schema, Option
from konvigius.exceptions import ( ConfigMetadataError, ConfigTypeError, 
                                   ConfigRangeError, ConfigValidationError,
                                   ConfigComputedFieldError, ConfigDomainError)

# ----------------------------
# Basic Tests
# ----------------------------

def test_instantion_default_raises():
    "raise: when no Schema is given"
    with pytest.raises(TypeError, match=re.escape(
         "Option.__init__() missing 1 required positional argument: 'entry'")):
        opt = Option()

def test_instantion_with_minimal_entry():
    "OK: only name is given"
    entry = Schema("username")
    cfg = Config.config_factory([entry])
    opt = cfg.get_meta("username")
    assert opt.name == "username"
    assert opt.short_flag is None
    assert opt.field_type is None
    assert opt.domain is None
    assert opt.default_value is None
    assert opt.r_min is None
    assert opt.r_max is None
    assert opt.fn_validator == tuple()
    assert opt.fn_computed == tuple()
    assert opt.help_text == "Help: username (default None)"
    assert opt.do_validate == True

def test_instantion_with_validation_False():
    "OK: only name is given"
    entry = Schema("username", no_validate=True)
    cfg = Config.config_factory([entry])
    opt = cfg.get_meta("username")
    print(opt)
    assert opt.name == "username"
    assert opt.short_flag is None
    assert opt.field_type is None
    assert opt.domain is None
    assert opt.default_value is None
    assert opt.r_min is None
    assert opt.r_max is None
    assert opt.fn_validator is None
    assert opt.fn_computed is None
    assert opt.help_text == "Help: username (default None)"
    assert opt.do_validate == False

def test_instantion_with_short_flag_in_name():
    "OK: only name is given"
    entry = Schema("username|u")
    cfg = Config.config_factory([entry])
    opt = cfg.get_meta("username")
    assert opt.name == "username"
    assert opt.short_flag == "u"
    assert opt.field_type is None
    assert opt.domain is None
    assert opt.default_value is None
    assert opt.r_min is None
    assert opt.r_max is None
    assert opt.fn_validator == tuple()
    assert opt.fn_computed == tuple()
    assert opt.help_text == "Help: username (default None)"
    assert opt.do_validate == True

def test_instantion_with_short_flag_in_name_2():
    "OK: only name is given"
    entry = Schema("username|u", short_flag="n")
    cfg = Config.config_factory([entry])
    opt = cfg.get_meta("username")
    assert opt.name == "username"
    assert opt.short_flag == "n"
    assert opt.field_type is None
    assert opt.domain is None
    assert opt.default_value is None
    assert opt.r_min is None
    assert opt.r_max is None
    assert opt.fn_validator == tuple()
    assert opt.help_text == "Help: username (default None)"
    assert opt.do_validate == True

def test_instantion_with_too_long_short_flag_in_name():
    "raises: short_flag to long"
    entry = Schema("username|us")
    with pytest.raises(ConfigMetadataError, match=re.escape(
         "short CLI flags must be a single character: 'us'")):
        cfg = Config.config_factory([entry])

def test_instantion_with_short_flag_in_name_3():
    "OK: short_flag to long but is replaced by explicit short_flag"
    entry = Schema("username|us", short_flag="u")
    cfg = Config.config_factory([entry])
    opt = cfg.get_meta("username")
    assert opt.name == "username"
    assert opt.short_flag == "u"
    assert opt.field_type is None
    assert opt.domain is None
    assert opt.default_value is None
    assert opt.r_min is None
    assert opt.r_max is None
    assert opt.fn_validator == tuple()
    print(opt.help_text)
    assert opt.help_text == "Help: username (default None)"
    assert opt.do_validate == True

def test_instantion_with_short_flag_in_name_4():
    "raises: no name"
    entry = Schema("|u")
    with pytest.raises(ConfigMetadataError, match=re.escape(
         "Schema name not valid (|u)")):
        cfg = Config.config_factory([entry])

# ----------------------------
# Validator Tests
# ----------------------------

def test_validate_name():
    "OK: only name is given"
    entry = Schema("username|u")
    cfg = Config.config_factory([entry])
    opt = cfg.get_meta("username")
    assert opt.name == "username"
    assert opt.short_flag == "u"

def test_validate_name_and_str():
    "OK: name is given and datatype is str"
    entry = Schema("username|u", field_type=str, default=1234, no_validate=True) # False is default
    cfg = Config.config_factory([entry])
    assert cfg.username == 1234

def test_validate_name_and_int():
    "Fail: name is given and datatype is int"
    entry = Schema("username|u", field_type=str, default=123)
    with pytest.raises(ConfigValidationError):
        cfg = Config.config_factory([entry])

def test_validate_name_and_int_NO_VALIDATE_1():
    "OK: only name is given, but datatype is INT"
    entry = Schema("username|u", field_type=int, no_validate=True) # False is default
    cfg = Config.config_factory([entry])
    assert cfg.username is None

def test_validate_name_and_int_NO_VALIDATE_2():
    "Fail: name is given and datatype is int AND wrong lenght short-flag"
    "Shortflag length must always be 1"
    entry = Schema("username|XXX", field_type=int, no_validate=True)
    with pytest.raises(ConfigMetadataError):
        cfg = Config.config_factory([entry])

@pytest.mark.parametrize("arg", [1,2,3,4,5])
def test_validate_int(arg):
    "OK: ints are in range"
    entry = Schema("username|u", r_min=1, r_max=5, default=arg)
    cfg = Config.config_factory([entry])
    assert cfg.username == arg

@pytest.mark.parametrize("arg", [-1, 0, 6, 7])
def test_validate_int_raises(arg):
    "FAIL: ints are not in range"
    entry = Schema("username|u", r_min=1, r_max=5, default=arg)
    with pytest.raises(ConfigRangeError):
        cfg = Config.config_factory([entry])

@pytest.mark.parametrize("arg", [(int, 0), (str,"a"), (float, 3.14), (list, [1,2]), (set, {1,2})])
def test_validate_multiple_types_1(arg):
    "OK: multiple types"
    entry = Schema("username|u", field_type=arg[0], default=arg[1])
    cfg = Config.config_factory([entry])
    assert cfg.username == arg[1]

@pytest.mark.parametrize("arg", [ 0,  "ab", [1,2] ])
def test_validate_multiple_types_2(arg):
    "OK: multiple types"
    entry = Schema("username|u", field_type=(int, str, list), default=arg)
    cfg = Config.config_factory([entry])
    assert cfg.username == arg

@pytest.mark.parametrize("arg", [ "ab", [1,2] ])
def test_validate_multiple_types_3(arg):
    "Fail: multiple types"
    entry = Schema("username|u", field_type=(float, set), default=arg)
    with pytest.raises(ConfigValidationError):
        cfg = Config.config_factory([entry])

@pytest.mark.parametrize("arg", [(int, "0"), (str,1), (float, 4), (list, "abc"), (set, [1,2])])
def test_validate_multiple_types_raises(arg):
    "raises: wrong types"
    entry = Schema("username|u", field_type=arg[0], default=arg[1])
    with pytest.raises(ConfigTypeError):
        cfg = Config.config_factory([entry])

@pytest.mark.parametrize("arg", ['guest', 'admin', 'finance'])
def test_validate_domain(arg):
    "OK: domain"
    entry = Schema("username|u", domain={'guest', 'admin', 'finance'}, default=arg )
    cfg = Config.config_factory([entry])
    assert cfg.username == arg

@pytest.mark.parametrize("arg", ['hacker', 'finance'])
def test_validate_domain_raises(arg):
    "FAIL: domain"
    entry = Schema("username|u", domain={'guest', 'admin'} , default=arg)
    with pytest.raises(ConfigValidationError):
        cfg = Config.config_factory([entry])

@pytest.mark.parametrize("arg", ['hacker', 0 , 1, [], [3,4], set(), 3.14, False, True ]) 
def test_validate_required(arg):
    "OK: required"
    entry = [Schema("username|u", required=True, default=arg)]
    cfg = Config.config_factory(entry)
    assert cfg.username == arg

def test_validate_required_raises():
    "Fail: required"
    entry = [Schema("username|u", required=True)]
    with pytest.raises(ConfigValidationError):
        Config.config_factory(entry)

def test_validate_type_and_domain():
    "OK: domain"
    entry = [Schema("username|u", default=123, domain={'guest', 123}, field_type=(str, int))]
    cfg = Config.config_factory(entry)
    assert cfg.username == 123

def test_validate_contradiction_type_and_domain():
    "OK: domain"
    entry = [Schema("username|u", default=3.14, domain={'guest', 123}, field_type=str )]
    with pytest.raises(ConfigTypeError):
        Config.config_factory(entry)

# === END ===
