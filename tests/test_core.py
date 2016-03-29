import explo.core
import pytest

def test_validate_invalid():
    """ Test invalid block (required field description/parameter missing) """
    invalid = """
    name: foobar
    module: modname
    """

    assert explo.core.validate_blocks([invalid]) == False

def test_validate_valid():
    """ Test a valid block """

    valid = """
    name: foobar
    module: modname
    description: description
    parameter:
    """

    assert explo.core.validate_blocks([valid])
