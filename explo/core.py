""" Main handler """
import click
import yaml
import logging

from importlib import import_module

VERSION = 0.1

class ExploException(Exception):
    """ Base class for exceptions """
    pass

class ParserException(ExploException):
    """ Exception thrown when parsing an explo yaml file failed """
    pass

class ResultException(ExploException):
    """ Exception thrown when problems occur regarding the result """
    pass

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@click.command()
@click.argument('files', nargs=-1)
@click.option('--verbose', is_flag=True)
@click.pass_context
def main(ctx, files, verbose):
    """ Get file list from args and execute """

    if len(files) <= 0:
        click.echo(main.get_help(ctx))

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.debug('Verbose mode')

    for filename in files:
        try:
            result = from_file(filename)

            if result:
                logger.info('Success (%s)', filename)
            else:
                logger.info('Failed (%s)', filename)
        except ExploException as exc:
            logger.error('error processing %s: %s', filename, exc)

def from_file(filename):
    """ Read file and pass to explo_content """

    try:
        fhandle = open(filename, 'r')
        content = fhandle.read()
    except IOError as err:
        raise ExploException('could not open file %s: %s' % (filename, err))

    return from_content(content)

def from_content(content):
    """ Load, validate and process blocks """

    try:
        blocks = load_blocks(content)
    except yaml.YAMLError as err:
        raise ExploException('error parsing document: %s' % err)

    validate_blocks(blocks)
    return proccess_blocks(blocks)

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

def proccess_blocks(blocks):
    """ Processes all blocks """

    scope = {}
    last_result = False

    for block in blocks:
        name = block['name']

        logger.debug("'===> Block '%s'", name)

        last_result, scope = module_execute(block, scope)

        if not last_result:
            return last_result

    return last_result

def module_execute(block, scope):
    """ Use corresponding module to process block """
    module = block['module']

    # dynamically load modules
    try:
        mod = import_module('explo.modules.%s' % module)
        return mod.execute(block, scope)
    except ImportError as exc:
        raise ExploException('[%s] module %s was not found.' % (module, exc))
    except ParserException as exc:
        raise ExploException('[%s] parsing error: %s' % (module, exc))
    except Exception as exc:
        raise ExploException('[%s] error: %s - %s' % (module, type(exc).__name__, exc))
