"""Set logging, get current host, read and configure API spec."""
import argparse
import importlib
import logging
import os
from pathlib import Path

import coloredlogs

import utils.errors as err
import utils.setup


def run():
    """Look for all test modules and run them."""
    testgroups = ['v101', 'v110']
    settings = utils.setup.Settings()
    for version in testgroups:
        logging.info(f'Testing version {version}')
        testdir = Path('tests') / version
        for path in testdir.glob('*.py'):
            module, _ = os.path.splitext(os.path.basename(path))
            if 'test' in module:
                logging.info('*** Running tests from %s', module)
                try:
                    importlib.import_module(f'tests.{version}.'+module)
                    logging.info('Module %s done ***\n', module)
                except err.BeaconTestError:
                    exit()
        if version == settings.version:
            # don't continue to higher versions
            break


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
    parser.add_argument('--one_based', action="store_true",
                        help="Expect the beacon to be 1 based")
    parser.add_argument('--version', nargs='?', default='v1.0.1',
                        choices=['v1.0.1', 'v1.1.0', 'v101', 'v110'],
                        help="Which version of the api to test. Defalt v1.0.1")

    c_args = parser.parse_args()
    if c_args.only_warn:
        coloredlogs.install(level='WARNING', fmt='%(levelname)s: %(message)s')
    try:
        utils.setup.Settings().set_args(c_args)
    except err.BeaconTestError:
        exit()
    run()
