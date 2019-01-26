""" Testing """
import argparse
import logging

import tests.beaconerrors_tests as beaconerrors_tests
import tests.query_tests as query_tests
import tests.specerrors_tests as specerrors_tests
import validate


HOSTS = {
    'local': 'http://localhost:5050',
    'sv': 'https://swefreq-dev.nbis.se/api/beacon-elixir/',
    'es': 'https://ega-archive.org/beacon-api',
    'fi': 'https://beaconpy-elixirbeacon.rahtiapp.fi/',
    }
SPEC = validate.parse_spec('beacon.yaml')


def test(host):
    """ Test the given host """
    logging.info('Testing %s', host)
    validate.validate_info(SPEC, host)
    make_test(beaconerrors_tests.tests, host, 400)
    make_test(specerrors_tests.tests, host, 400, validate_query=False)
    make_test(query_tests.tests, host, 200)


def make_test(tests, host, status_code=200, validate_query=True):
    """ Run a serie of tests that all should return the given status code
        Each test consists of a query and an expected response
        The query answer should contain everything in the expected response
    """
    for testf in tests:
        test_q, gold = testf()
        logging.info('Testing %s', testf.__name__)
        errors = validate.validate_call(SPEC, host, test_q, validate_query=validate_query,
                                        code=status_code, gold=gold)
        for error in errors:
            logging.error('\tAn error %s', error)
        logging.info('Done')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, nargs='?', default='local')
    args = parser.parse_args()
    hosturl = HOSTS.get(args.host, HOSTS.get('local'))
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    logging.info('Testing host %s', hosturl)
    test(hosturl)
