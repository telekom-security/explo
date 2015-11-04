import explo.core
import pytest

def test_validate_invalid():
    """ Test invalid block (required field description/parameter missing) """
    invalid = """
    name: foobar
    module: modname
    """

    with pytest.raises(Exception):
        explo.core.validate_blocks([invalid])

def test_validate_valid():
    """ Test a valid block """

    valid = """
    name: foobar
    module: modname
    description: description
    parameter:
    """

    explo.core.validate_blocks([valid])
