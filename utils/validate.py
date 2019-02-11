"""
Module responsible for validating queries and replies
Uses openapi_core to validate against the api specification
Comparisions of the status code and the result data
"""
import json
import logging
from operator import itemgetter
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
        logging.info('Testing %s\n %s', func.__name__, func.__doc__)
        errors = validate_call(spec, host, path, query,
                               test_query=test_query,
                               code=code, gold=resp)
        for error in errors:
            logging.error(error)
        logging.info('Done\n')
    return decorator


class BeaconRequest(BaseOpenAPIRequest):
    """ Wrapper for a Request
    The url can be opened using the open method
    """
    def __init__(self, host, method, path, args=None,
                 view_args=None, headers=None, data=None,
                 mimetype='application/json'):
        make_offset(args)
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
    """ Wrapper for a Response
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
    in the other
    """
    errs = []
    compare_obj(gold, obj, errs)
    return errs


def compare_obj(gold, obj, err):
    """ Help function to compare(), compares objects """
    for key, val in gold.items():
        if not key in obj:
            err.append(f'Value missing: {key}  {obj.keys()}')
        if isinstance(val, dict):
            compare_obj(val, obj[key], err)
        elif isinstance(val, list):
            compare_list(sortlist(val, key), sortlist(obj[key], key), err)
        elif isinstance(val, float):
            if round(val, config.config.PRECISION) != round(obj[key], config.config.PRECISION):
                err.append(f'Bad value {key}: {val} != {obj[key]}')
        else:
            if val != obj[key]:
                err.append(f'Bad value {key}: {val} != {obj[key]}')


def compare_list(gold, clist, err):
    """ Help function to compare(), compares lists
        Assums that the two lists are ordered the same way
    """
    for n, item in enumerate(gold):
        if len(clist) <= n:
            err.append(f'Result list too short. {item} not in {clist}')
            break
        if isinstance(item, dict):
            compare_obj(item, clist[n], err)
        elif isinstance(item, list):
            compare_list(sortlist(item), sortlist(clist[n]), err)
        else:
            if item not in clist:
                err.append(f'{item} not in {clist}')


def sortlist(inp, key=''):
    """ Sort lists
    Lists of dictionaries will be sorted as defined in the configurations
    Logs a warning if the list cannot be properly sorted
    """
    sorter = config.config.SORT_BY.get(key)
    if sorter and inp and isinstance(inp[0], dict):
        return sorted(inp, key=itemgetter(sorter))
    if inp and isinstance(inp[0], dict):
        logging.warning('Could not sort list %s', inp)
        return inp

    return sorted(inp)


def make_offset(args):
    """ Shift start & end position to adjust for 0-based beacons """
    for key in ['start', 'end', 'startMin', 'startMax', 'endMin', 'endMax']:
        if config.config.START_POS == 0:
            if key in args:
                args[key] = max(args[key]-1, 0)
