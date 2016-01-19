""" Core HTTP functionalities """
import click

def execute(block, scope=None, debug=False):
    """ Match results """
    required_fields = ['type', 'value']

    if not all(k in block['parameter'] for k in required_fields):
        raise Exception('not all required parameters were passed')

    opts = block['parameter']

    source_module, source_dict, source_field = block['source'].split('.')

    try:
        content = scope[source_module][source_dict][source_field]
    except Exception:
        raise Exception('the source field "%s" was not found in the current scope' % block['source'])

    click.echo("Matching %s for: '%s'" % (block['source'], opts['value']))

    success = False

    if opts['type'] == 'stringcompare' and content == opts['value']:
        success = True

    if opts['type'] == 'stringfind' and opts['value'] in content:
        success = True

    return success, scope
