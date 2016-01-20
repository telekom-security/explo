""" Main handler """
import click
import yaml
from importlib import import_module
from colorama import Fore, init

class ExploException(Exception):
    """ Base class for exceptions """
    pass

class ParserException(ExploException):
    """ Exception thrown when parsing an explo yaml file failed """
    pass

@click.command()
@click.argument('files', nargs=-1)
@click.option('--debug', is_flag=True)
@click.pass_context
def main(ctx, files, debug):
    """ Get file list from args and execute """

    init(autoreset=True)

    if len(files) <= 0:
        click.echo(main.get_help(ctx))

    for filename in files:
        try:
            result = from_file(filename, debug)

            if result:
                click.echo(Fore.GREEN + "===> Success ({})".format(filename))
            else:
                click.echo(Fore.RED + "===> Failed ({})".format(filename))
        except ExploException as exc:
            click.echo(Fore.RED + 'error processing {}: {}'.format(filename, exc))


def from_file(filename, debug):
    """ Read file and pass to explo_content """

    try:
        fhandle = open(filename, 'r')
        content = fhandle.read()
    except IOError as err:
        return ExploException('could not open file %s: %s' % (filename, err))

    return from_content(content, debug)

def from_content(content, debug):
    """ Load, validate and process blocks """

    try:
        blocks = load_blocks(content)
    except yaml.YAMLError as err:
        return ExploException('error parsing document: %s' % err)

    validate_blocks(blocks)
    return proccess_blocks(blocks, debug)

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
            raise ParserException('not all required field in block %d' % count)

def proccess_blocks(blocks, debug=False):
    """ Processes all blocks """

    scope = {}
    last_result = False

    for block in blocks:
        name = block['name']

        if debug:
            click.echo(Fore.YELLOW + "===> Block '%s'" % name)

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
