""" Main handler """
import click
import yaml
from importlib import import_module
from colorama import Fore, init

class ExploException(Exception):
    pass

class ResultException(ExploException):
    pass

@click.command()
@click.argument('files', nargs=-1)
@click.option('--debug', is_flag=True)
@click.pass_context
def main(ctx, files, debug):
    """ Get file list from args and execute """

    init(autoreset=True)

    if len(files) <= 0:
        print(main.get_help(ctx))

    for filename in files:
        explo_file(filename, debug)

def explo_file(filename, debug):
    """ Parse file and execute blocks """

    try:
        fhandle = open(filename, 'r')
        content = fhandle.read()
    except IOError as err:
        return print('could not open file %s: %s' % (filename, err))

    try:
        blocks = load_blocks(content)
    except yaml.YAMLError as err:
        return print('error parsing document: %s' % err)

    validate_blocks(blocks)
    result = proccess_blocks(blocks, debug)

    if result:
        print(Fore.GREEN + "===> Success ({})".format(filename))
    else:
        print(Fore.RED + "===> Failed ({})".format(filename))

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
