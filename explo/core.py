""" Main handler """
import sys
import click
import yaml

from eliot import Message, to_file, add_destination

from explo.modules import http as module_http, http_header as module_header
from explo.exceptions import ExploException, ParserException

VERSION = 0.1
FIELDS_REQUIRED = ['name', 'description', 'module', 'parameter']

@click.command()
@click.argument('files', nargs=-1)
@click.option('--verbose', is_flag=True)
@click.pass_context
def main(ctx, files, verbose):
    """ Get file list from args and execute """

    if len(files) <= 0:
        click.echo(main.get_help(ctx))

    if verbose:
        add_destination(log_stdout)

    for filename in files:
        try:
            if from_file(filename):
                print('Success (%s)' % filename)
            else:
                print('Failed (%s)', filename)

        except ExploException as exc:
            print('error processing %s: %s', filename, exc)

def from_file(filename, log_file=None):
    """ Read file and pass to from_content """

    try:
        fhandle = open(filename, 'r')
        content = fhandle.read()
    except IOError as err:
        raise ExploException('could not open file %s: %s' % (filename, err))

    return from_content(content, log_file)

def from_content(content, log_file=None):
    """ Load, validate and process blocks """

    try:
        blocks = load_blocks(content)
    except yaml.YAMLError as err:
        raise ExploException('error parsing document: %s' % err)

    if not validate_blocks(blocks):
        raise ExploException('error parsing document: not all blocks specify the required fields %s' % FIELDS_REQUIRED)

    if log_file:
        to_file(log_file)

    return process_blocks(blocks)

def load_blocks(content):
    """ Load documents/blocks from a YAML file """
    return [b for b in yaml.safe_load_all(content)]

def validate_blocks(blocks):
    """ Ensures minimal fields for blocks """

    for block in blocks:

        if not all(k in block for k in FIELDS_REQUIRED):
            return False

    return True

def process_blocks(blocks):
    """ Processes all blocks """

    scope = {}
    last_result = False

    for block in blocks:
        name = block['name']

        Message.log(level='status', message='Processing block %s' % name)

        last_result, scope = module_execute(block, scope)

        if not last_result:
            return last_result

    return last_result

def module_execute(block, scope):
    """ Use corresponding module to process block """
    module = block['module']

    modules = {
        "http": module_http,
        "header": module_header
    }

    if not module in modules:
        raise ExploException('This module is not allowed')

    try:
        return modules.get(module).execute(block, scope)
    except ParserException as exc:
        raise ExploException('[%s] parsing error: %s' % (module, exc))
    except Exception as exc:
        print(exc)
        raise ExploException(exc)

def log_stdout(message):
    if 'message' in message:
        print("DEBUG: ", message['message'])
