""" Core HTTP functionalities """

def execute(block, scope=None):
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

    print("Matching %s for: '%s'" % (block['source'], opts['value']))

    if opts['type'] == 'stringcompare':
        return content == opts['value']

    if opts['type'] == 'stringfind':
        return opts['value'] in content

    return False
