"""
Module responsible for validating queries and replies
Uses openapi_core to validate against the api specification
Comparisions of the status code and the result data
"""
import json
import logging
import urllib.request
import urllib.parse

from openapi_core.shortcuts import RequestValidator, ResponseValidator
from openapi_core.wrappers.base import BaseOpenAPIRequest, BaseOpenAPIResponse
from werkzeug.datastructures import ImmutableMultiDict

import config.config
import utils.setup
import utils.jsonschemas


def validate_query(code, path='query', test_query=False):
    """ Decorator for test queries.
        A function decorated with this should return a
        query (dict) and an expected result (dict)
    """
    host, spec = utils.setup.setup()

    def decorator(func):
        query, resp = func()
        logging.info('Testing %s', func.__name__, )
        errors = validate_call(spec, host, path, query,
                               test_query=test_query,
                               code=code, gold=resp)
        for error in errors:
            logging.error(error)
        logging.info('Done')
    return decorator


class BeaconRequest(BaseOpenAPIRequest):
    """
    Wrapper for a Request
    The url can be opened using the open method
    """
    def __init__(self, host, method, path, args=None,
                 view_args=None, headers=None, data=None,
                 mimetype='application/json'):
        self.host_url = host
        self.path = path
        self.path_pattern = path #parsed.path + path
        self.method = method.lower()

        self.parameters = {
            'path': view_args or {},
            'query': ImmutableMultiDict(args or []),
            'header': headers or {},
            'cookie': {},
        }
        self.body = data or ''
        self.mimetype = mimetype

    @property
    def full_url_pattern(self):
        url = '/'+self.path_pattern
        if url.endswith('//'):
            url = url[:-1]
        return url

    def open(self):
        """ Open the url """
        url = '/'.join([self.host_url, self.path_pattern])
        if url.endswith('//'):
            url = url[:-1]
        query = urllib.parse.urlencode(self.parameters['query'])
        if query:
            url += f'?{query}'
        logging.info('Open %s', url)
        return urllib.request.urlopen(url)


class BeaconResponse(BaseOpenAPIResponse):
    """
    Wrapper for a Response
    Stores the response body, error code and the content type
    """
    def __init__(self, request):
        self.error = False
        try:
            response = request.open()
            # pdb.set_trace()
            self.data = response.read()
            self.status_code = response.getcode()
            self.mimetype = response.info().get_content_type()

        except urllib.error.HTTPError as err:
            self.status_code = err.getcode()
            self.mimetype = err.info().get_content_type()
            self.data = err.read()
            self.error = True


def validate_call(spec, host, path, query, test_query=True, code='', gold=None):
    """ Validate a query and its response """
    req = BeaconRequest(host, 'GET', path, args=query)
    errors = []
    if test_query:
        # check that the query complies to the api spec
        validator = RequestValidator(spec)
        result = validator.validate(req)
        errors.extend(result.errors)
        # validate against jsons schemas
        errors.extend(utils.jsonschemas.validate(req.body, 'query'))

    # check that the response complies to the api spec
    resp = BeaconResponse(req)
    validator = ResponseValidator(spec)
    result = validator.validate(req, resp)
    errors.extend(result.errors)

    # validate against json schemas
    errors.extend(utils.jsonschemas.validate(resp.data, 'response', path, error=resp.error))

    if code and resp.status_code != code:
        errors += [f'Unexpected http code {resp.status_code}. Expected: {code}']

    if gold is None:
        gold = {}
    err = compare(gold, json.loads(resp.data))
    errors.extend(err)
    return errors


def print_errors(result):
    """ Print errors """
    for error in result.errors:
        logging.error('\t%s', error)


def compare(gold, obj):
    """ Compare two objects to see that everything in the gold object is also
    in the other """
    try:
        compare_obj(gold, obj)
    except AssertionError as err:
        return [str(err)]
    return []


def compare_obj(gold, obj):
    """ Help function to compare(), compares objects """
    for key, val in gold.items():
        assert key in obj, 'Value missing: %s   %s' % (key, obj.keys)
        if isinstance(val, dict):
            compare_obj(val, obj[key])
        elif isinstance(val, list):
            compare_list(val, obj[key])
        elif isinstance(val, float):
            assert round(val, config.config.PRECISION) == \
                   round(obj[key], config.config.PRECISION), 'Bad value: %s != %s' % (val, obj[key])
        else:
            assert val == obj[key], 'Bad value: %s != %s' % (val, obj[key])


def compare_list(gold, clist):
    """ Help function to compare(), compares lists
        Assums that the two lists are ordered the same way
    """
    for n, item in enumerate(gold):
        assert len(clist) > n, 'Result list too short. %s not in %s' % (item, clist)
        if isinstance(item, dict):
            compare_obj(item, clist[n])
        elif isinstance(item, list):
            compare_list(item, clist[n])
        else:
            assert item in clist, '%s not in %s' % (item, clist)
