import explo.core
import pytest

block = """
name: metadata
module: metadata
parameter:
  foo: bar
  foobar: 1.0
"""

def test_metadata_valid():
    """ Test a metadata block """
    blocks = explo.core.load_blocks(block)
    assert explo.core.validate_blocks(blocks) == True

def test_metadata_func():
    """ Test return value of meta_from_content """
    assert explo.core.meta_from_content(block) == {'foo': 'bar', 'foobar': 1.0}
