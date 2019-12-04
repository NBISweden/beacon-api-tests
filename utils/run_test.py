"""Module for running tests, specified in yml."""

import logging

from utils.beacon_query import call_beacon
import utils.errors as err
from utils.compare import assert_partly_in, assert_not_in
import utils.setup


def run_test(test):
    """Call the beacon as specified in the test and check the result."""
    logging.info(f"Running test {test['name']}")
    logging.debug(f"{test.get('descr', '')}")
    logging.debug(f"Assuming that this data is present in your beacon: {test.get('data', [])}")
    settings = utils.setup.Settings()
    if test.get('skip', False):
        return
    try:
        if 'query' not in test:
            resp = call_beacon(path='/')
        else:
            resp = call_beacon(query=prepare_query(test['query']))

        for check in test['results']:
            assert_test(check, resp)

    except err.ResponseError as r_error:
        # errors from the comparisons of a response, contains a list of errors to report
        logging.error('Test "%s" did not pass: """%s"""', test['name'], test['descr'])
        for err_msg in r_error.messages:
            settings.errors += 1
            logging.error(err_msg)

    except AssertionError as a_error:
        # other errors
        logging.error('Test "%s" did not pass: """%s"""', test['name'], test['descr'])
        logging.error(str(a_error))
        settings.errors += 1


def assert_test(check, response):
    """Test one property."""
    assert check['property'] in response, f"{check['property']} not found in response"
    if check["assert"] == "isfalse":
        assert not response[check['property']], f"{check['property']} should be false"

    if check["assert"] == "length_eq":
        assert len(response[check['property']]) == check['count'], \
            f"Bad length of field {check['property']}" \
            f"should be {check['count']}, but is {len(response[check['property']])}"

    if check["assert"] == "contains":
        assert_partly_in(check['data'], response, check['property'])

    if check["assert"] == "not_contains":
        assert_not_in(check['data'], response, check['property'])


def prepare_query(query):
    """Remove all null values from the query."""
    empties = [key for (key, val) in query.items() if val is None]
    for key in empties:
        del query[key]
    return query
