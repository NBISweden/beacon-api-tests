""" Set logging, get current host, read and configure API spec """
import argparse
import glob
import importlib
import logging
import os

import coloredlogs

import utils.setup


def run():
    """ Look for all test modules and run them """
    for path in glob.glob('tests/*py'):
        module, _ = os.path.splitext(os.path.basename(path))
        if 'test' in module:
            logging.info('*** Running tests from %s', module)
            importlib.import_module('tests.'+module)
            logging.info('Module %s done ***\n', module)


if __name__ == '__main__':
    coloredlogs.install(level='INFO', fmt='%(levelname)s: %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, nargs='?', default='local')
    parser.add_argument('--no_openapi', action="store_true")
    parser.add_argument('--no_json', action="store_true")
    parser.add_argument('--only_structure', action="store_true")
    utils.setup.Settings().set_args(parser.parse_args())
    run()
