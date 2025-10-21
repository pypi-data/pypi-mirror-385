# tests/test_class_Schema.py
import re
import pytest
from typing import Any
import types

from dataclasses import dataclass, field

from konvigius.configlib import Schema

# ----------------------------
# Fixtures & Helpers
# ----------------------------


# ----------------------------
# Basic Tests
# ----------------------------

def test_instantion_default_raises():
    "raise: when no name is given"
    with pytest.raises(TypeError, match=re.escape(
         "Schema.__init__() missing 1 required positional argument: 'name'")):
        entry = Schema()

def test_instantion_name_only():
    "OK: only name is given"
    entry = Schema("username")
    assert entry.name == "username"
    assert entry.short_flag is None
    assert entry.field_type is None
    assert entry.default is None
    assert entry.r_min is None
    assert entry.r_max is None
    assert entry.domain is None
    assert entry.fn_validator is None
    assert entry.help_text is None
    assert entry.no_validate is False

def test_instantion_keyword_raises():
    # "raise: only 1 positional parameter allowed"
    with pytest.raises(TypeError, match=re.escape(
          "Schema.__init__() takes 2 positional arguments but 3 were given")):
        entry = Schema("username", "u")

def test_instantion_some_arguments_1():
    "OK: only name is given"
    entry = Schema("username",
                        short_flag="u",
                        default="guest")

    assert entry.name == "username"
    assert entry.short_flag == "u"
    assert entry.field_type is None
    assert entry.default == "guest"
    assert entry.required is None
    assert entry.r_min is None
    assert entry.r_max is None
    assert entry.fn_validator is None
    assert entry.help_text is None
    assert entry.no_validate is False

def test_instantion_all_arguments_1():
    "OK: only name is given"
    entry = Schema("timeout",
                         short_flag="t",
                         field_type=int,
                         required=True,
                         default=10,
                         r_min=1,
                         r_max=10,
                         domain={'a', 2 , '3'},
                         fn_validator=lambda x: "return this string",
                         help_text="Timeout help")

    assert entry.name == "timeout"
    assert entry.short_flag == "t"
    assert entry.field_type is int
    assert entry.required is True
    assert entry.default == 10
    assert entry.r_min == 1 
    assert entry.r_max == 10
    assert entry.domain == {'a', 2 , '3'}
    assert entry.help_text == "Timeout help"
    assert entry.no_validate is False
    assert isinstance(entry.fn_validator, types.FunctionType)

# === END ===
