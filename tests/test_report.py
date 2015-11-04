import explo.core
from explo.modules import report

def test_report_match():
    """ Test the stringcompare """
    valid = """
name: result
description: match
module: report
source: exploit.extracted.compareTest
parameter:
    type: stringcompare
    value: foobar
    """

    scope = {
        'exploit': {
            'extracted': {
                'compareTest': 'foobar'
            }
        }
    }

    blocks = explo.core.load_blocks(valid)

    ret = report.execute(blocks[0], scope)

    assert ret

def test_report_find():
    """ Test the stringfind """
    valid = """
name: result
description: match
module: report
source: exploit.extracted.compareTest
parameter:
    type: stringfind
    value: error in your SQL
    """

    scope = {
        'exploit': {
            'extracted': {
                'compareTest': 'error: You have an error in your SQL syntax.'
            }
        }
    }

    blocks = explo.core.load_blocks(valid)

    ret = report.execute(blocks[0], scope)

    assert ret
