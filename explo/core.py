""" Main handler """
import click
import yaml
import sys
from importlib import import_module
from colorama import Fore, init

class ExploException(Exception):
    pass

class ResultException(ExploException):
    pass

@click.command()
@click.argument('filename')
@click.option('--debug', is_flag=True)
def main(filename, debug):
    """ Read file and process blocks """

    init(autoreset=True)

    try:
        fhandle = open(filename, 'r')
        content = fhandle.read()
    except IOError as err:
        sys.exit('could not open file %s: %s' % (filename, err))

    try:
        blocks = load_blocks(content)
    except yaml.YAMLError as err:
        sys.exit('error parsing document: %s' % err)

    validate_blocks(blocks)
    result = proccess_blocks(blocks, debug)

    if result:
        print(Fore.GREEN + "===> Success")
    else:
        print(Fore.RED + "===> Failed")

def load_blocks(content):
    """ Load documents/blocks from a YAML file """
    return [b for b in yaml.safe_load_all(content)]

def validate_blocks(blocks):
    """ Ensures minimal fields for blocks """

    count = 0

    for block in blocks:
        count += 1
        required_fields = ['name', 'description', 'module', 'parameter']

        if not all(k in block for k in required_fields):
            raise ExploException('not all required field in block %d' % count)

def proccess_blocks(blocks, debug=False):
    """ Processes all blocks """

    scope = {}
    last_result = False

    for block in blocks:
        name = block['name']
        print(Fore.YELLOW + "===> Block '%s'" % name)

        last_result, scope = module_execute(block, scope, debug)

        if not last_result:
            return last_result

    return last_result

def module_execute(block, scope, debug):
    """ Use corresponding module to process block """
    module = block['module']

    # dynamically load modules
    try:
        mod = import_module('explo.modules.%s' % module)
        return mod.execute(block, scope, debug)
    except Exception as exc:
        raise ExploException('[%s] module exception: %s' % (module, exc))
