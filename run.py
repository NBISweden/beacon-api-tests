""" Set logging, get current host, read and configure API spec """
import argparse
import glob
import importlib
import logging
import os

import coloredlogs

import utils.errors as err
import utils.setup


def run():
    """ Look for all test modules and run them """
    for path in glob.glob('tests/*py'):
        module, _ = os.path.splitext(os.path.basename(path))
        if 'test' in module:
            logging.info('*** Running tests from %s', module)
            try:
                importlib.import_module('tests.'+module)
                logging.info('Module %s done ***\n', module)
            except err.BeaconTestError:
                exit()


if __name__ == '__main__':
    coloredlogs.install(level='INFO', fmt='%(levelname)s: %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, nargs='?', default='local',
                        help="Specify which beacon host to test")
    parser.add_argument('--no_openapi', action="store_true",
                        help="Don't validate against the OpenAPI specification")
    parser.add_argument('--no_json', action="store_true",
                        help="Don't validate against the JSON Schemas")
    parser.add_argument('--only_structure', action="store_true",
                        help="Don't validate the resulting counts, frequencies etc")
    parser.add_argument('--only_warn', action="store_true",
                        help="Only print warnings and errors")

    c_args = parser.parse_args()
    if c_args.only_warn:
        coloredlogs.install(level='WARNING', fmt='%(levelname)s: %(message)s')
    try:
        utils.setup.Settings().set_args(c_args)
    except err.BeaconTestError:
        exit()
    run()
