import explo.core
import pytest

def test_load_blocks():
    """ Test invalid block (required field description/parameter missing) """
    block = """
    name: foobar
    module: modname
    description: foo
    parameter:
    """
    blocks = explo.core.load_blocks(block)

    assert len(blocks) == 1

def test_validate_invalid():
    """ Test invalid block (required field description/parameter missing) """
    invalid = """
    name: foobar
    module: modname
    """
    blocks = explo.core.load_blocks(invalid)

    assert explo.core.validate_blocks(blocks) == False

def test_validate_valid():
    """ Test a valid block """
    valid = """
    name: foobar
    module: modname
    description: description
    parameter:
    """
    blocks = explo.core.load_blocks(valid)

    assert explo.core.validate_blocks(blocks)
