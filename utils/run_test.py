"""Module for running tests, specified in yml."""

import logging
import operator

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
        status_code, ignore_schemas = prepare_call(test)
        if 'query' not in test:
            resp = call_beacon(path='/', code=status_code, ignore_schemas=ignore_schemas)
        else:
            query = prepare_query(test['query'])
            resp = call_beacon(query=query, code=status_code, ignore_schemas=ignore_schemas)

        if settings.check_result:
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


def prepare_call(test):
    """Check what http statuscode the test should result in, and whether query is valide."""
    status_code, ignore_schemas = 200, False
    for check in test['results']:
        if check["assert"] == "status_code":
            status_code = check.get('status_code', 200)
            ignore_schemas = check.get('ignore_schemas', False)
    return status_code, ignore_schemas


def assert_test(check, response):
    """Test one property."""
    # assert check['property'] in response, f"{check['property']} not found in response"
    #if check["assert"] == "isfalse":
    #    assert not response[check['property']], f"{check['property']} should be false"
    length_ops = {'length_gt': (operator.gt, 'greater than'),
                  'length_lt': (operator.lt, 'lesser than'),
                  'length_eq': (operator.eq, 'equal to')
                  }

    if check["assert"] in length_ops:
        lop, txt = length_ops[check["assert"]]
        assert lop(len(response[check['property']]), check['length']), \
            f"Bad length of field {check['property']}" \
            f"should be {txt} {check['length']}, but is {len(response[check['property']])}"

    if check["assert"] == "contains":
        assert_partly_in(check['data'], response, check['property'])

    if check["assert"] == "not_contains":
        assert_not_in(check['data'], response, check['property'])

    if check["assert"] in ["is_true", "is_false"]:
        prop = response[check['property']]
        err_msg = f"Bad value of field {check['property']}" \
                  f"should be 'false', but is {response[check['property']]}"
        if check["assert"] == "is_false":
            prop = not prop
        assert prop, err_msg


def prepare_query(query):
    """Remove all null values from the query."""
    empties = [key for (key, val) in query.items() if val is None]
    for key in empties:
        del query[key]
    return query
