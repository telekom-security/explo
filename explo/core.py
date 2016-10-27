import argparse
import yaml

from eliot import Message, add_destination

from explo.modules import (
    http as module_http,
    http_header as module_header,
    sqli_blind as module_sqli
)
from explo.exceptions import ExploException, ParserException, ConnectionException, ProxyException
from explo import color

VERSION = 0.1
FIELDS_REQUIRED = ['name', 'description', 'module', 'parameter']

parser = argparse.ArgumentParser(description='Explo v{}'.format(VERSION))
parser.add_argument('filename', nargs='+',
                    help='Files to test')
parser.add_argument('-v', '--verbose', action='store_true',
                    help='Activate verbose output')

args = None

def main():
    """ Get file list from args and execute """
    global args

    args = parser.parse_args()
    add_destination(log_stdout)

    for filename in args.filename:
        try:
            print('Loading {}'.format(color.cyan(filename)))

            if from_file(filename):
                result = color.green('Success.')
            else:
                result = color.red('No match.')

            print('==> {}'.format(result))

        except ParserException as exc:
            print(color.yellow('ERROR parsing file %s: %s' % (filename, exc)))
        except (ConnectionException, ProxyException) as exc:
            print(color.yellow('ERROR connecting to host in file %s: %s' % (filename, exc)))
        except ExploException as exc:
            print(color.yellow('ERROR in file %s: %s' % (filename, exc)))

def from_file(filename, log=None):
    """ Read file and pass to from_content """

    try:
        with open(filename, 'r') as fhandle:
            content = fhandle.read()
    except IOError as err:
        raise ExploException('could not open file %s: %s' % (filename, err))

    return from_content(content, log)

def from_content(content, log=None):
    """ Load, validate and process blocks """

    if not content:
        raise ExploException('no exploitation content')

    try:
        blocks = load_blocks(content)
    except yaml.YAMLError as err:
        raise ExploException('error parsing document: %s' % err)

    if not validate_blocks(blocks):
        raise ExploException('error parsing document:' \
            'not all blocks specify the required fields %s' % FIELDS_REQUIRED)

    if log:
        add_destination(log)

    return process_blocks(blocks)

def load_blocks(content):
    """ Load documents/blocks from a YAML file """
    return [b for b in yaml.safe_load_all(content)]

def validate_blocks(blocks):
    """ Ensures minimal fields are set for passed block """

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
        desc = block['description']

        Message.log(level='status', message='Block {}: {}'.format(name, desc))

        last_result, scope = module_execute(block, scope)

        if not last_result:
            return last_result

    return last_result

def module_execute(block, scope):
    """ Use corresponding module to process block """
    module = block['module']

    modules = {
        'http': module_http,
        'header': module_header,
        'sqli_blind': module_sqli
    }

    if not module in modules:
        raise ExploException('This module is not allowed (%s)' % module)

    return modules.get(module).execute(block, scope)

def log_stdout(message):
    if 'message' in message:

        level = message.get('level', '')
        if level == 'request' or level == 'response':
            if args and not args.verbose:
                return

            print('\n')

        print(message['message'])
