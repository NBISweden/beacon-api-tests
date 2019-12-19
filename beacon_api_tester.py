"""Set logging, get current host, read and configure API spec."""
import argparse
import logging

import coloredlogs

import utils.errors as err
import utils.export as export
import utils.jsonschemas
import utils.run_test
import utils.setup


def run():
    """Look for all test modules and run them."""
    settings = utils.setup.Settings()
    for test in settings.tests:
        try:
            utils.run_test.run_test(test)
        except err.BeaconTestError:
            logging.error('Testing stopped unexpectedly.')
            exit()


def print_result():
    """Print a summary of the results."""
    settings = utils.setup.Settings()
    coloredlogs.install(level='DEBUG', fmt='%(message)s')
    logging.info(f'\n\n{"":_^40}')
    logging.info('Testing done. Result:\n')
    if settings.errors:
        logging.error(f'  {"Data errors:":27} {settings.errors} tests failed')
    if settings.warnings:
        logging.warning(f'  {"Specification errors:":27} {len(settings.warnings)} ({len(set(settings.warnings))} unique)')
    if settings.query_warnings:
        logging.warning(f'  {"Query specification errors:":27} {len(settings.query_warnings)} ({len(set(settings.query_warnings))} unique)')
    if not (settings.errors or settings.warnings or settings.query_warnings):
        logging.debug('  All tests passed!')
    logging.info('\n\n')


if __name__ == '__main__':
    coloredlogs.install(level='INFO', fmt='%(levelname)s: %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, nargs='?', default='local',
                        help="Specify which beacon host to test")
    parser.add_argument('--test', action='append',
                        help="Run a test (pathname for test configuration file in YAML format). "
                        "This option may occur several times")
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
    parser.add_argument('--validate_tests', action='append',
                        help="Check if a test file is correctly formatted."
                        "Input: pathname for test configuration file in YAML format."
                        "This option may occur several times")
    parser.add_argument('--extract_csv_data', action='append',
                        help="Extract the beacon data for a test."
                        "Input: pathname for test configuration file in YAML format.")
    # currently not used:
    parser.add_argument('--version', nargs='?', default='v1.0.1',
                        choices=['v1.0.1', 'v1.1.0', 'v101', 'v110'],
                        help="Which version of the api to test. Defalt v1.0.1")

    c_args = parser.parse_args()
    if c_args.validate_tests:
        utils.jsonschemas.run_testvalidaton(c_args.validate_tests)
        exit()
    if c_args.extract_csv_data:
        print(export.export_csv_testdata(c_args.extract_csv_data))
        exit()

    logging.info('Running api tests...')
    if c_args.only_warn:
        coloredlogs.install(level='WARNING', fmt='%(levelname)s: %(message)s')
    try:
        utils.setup.Settings().set_args(c_args)
    except err.BeaconTestError:
        exit()
    run()
    print_result()
