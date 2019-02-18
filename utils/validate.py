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

    def decorator(func):
        query, resp = func()
        logging.info('Testing %s\n      %s', func.__name__, func.__doc__.strip())
        errs, warns = validate_call(path, query,
                                    test_query=test_query,
                                    code=code, gold=resp)
        for error in errs:
            logging.error(error)
        for warn in warns:
            logging.warning(warn)
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
            self.data = response.read()
            self.status_code = response.getcode()
            self.mimetype = response.info().get_content_type()

        except urllib.error.HTTPError as err:
            self.status_code = err.getcode()
            self.mimetype = err.info().get_content_type()
            self.data = err.read()
            self.error = True


def validate_call(path, query, test_query=True, code='', gold=None):
    """ Validate a query and its response """
    settings = utils.setup.Settings()
    req = BeaconRequest(settings.host, 'GET', path, args=query)
    errors, warnings = [], []
    if test_query and settings.openapi:
        # check that the query complies to the api spec
        validator = RequestValidator(settings.openapi)
        result = validator.validate(req)
        warnings.extend(result.errors)

    if test_query and settings.use_json_schemas:
        # validate against jsons schemas
        warnings.extend(utils.jsonschemas.validate(req.body, 'query', settings))

    resp = BeaconResponse(req)
    if settings.openapi:
        # check that the response complies to the api spec
        validator = ResponseValidator(settings.openapi)
        result = validator.validate(req, resp)
        warnings.extend(result.errors)

    if settings.use_json_schemas:
        # validate against json schemas
        warnings.extend(utils.jsonschemas.validate(resp.data, 'response',
                                                   settings, path, error=resp.error))

    if code and resp.status_code != code:
        errors += [f'Unexpected http code {resp.status_code}. Expected: {code}']

    if gold is None:
        gold = {}
    if settings.check_result:
        err = compare(gold, json.loads(resp.data))
        errors.extend(err)
    return errors, warnings


def make_offset(args):
    """ Shift start & end position to adjust for 0-based beacons """
    for key in ['start', 'end', 'startMin', 'startMax', 'endMin', 'endMax']:
        if config.config.START_POS == 0:
            if key in args:
                args[key] = max(args[key]-1, 0)


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
        if key not in obj:
            err.append(f'Value missing: {key}  {obj.keys()}')
        if isinstance(val, dict):
            compare_obj(val, obj[key], err)
        elif isinstance(val, list):
            compare_list(val, obj[key], err, key)
        else:
            if normalize(val) != normalize(obj[key]):
                err.append(f'Bad value {key}: {val} != {obj[key]}')


def compare_objlist(gold, clist, sorter, err):
    """ Help function to compare(), compares a list of objects
        where each object can be identified by looking at a given key
    """
    for item in gold:
        if sorter not in item:
            err.append(f'No value for {sorter} in {item}, cannot compare')
            continue
        try:
            list_id = normalize(item[sorter])
            nextcomp = [obj for obj in clist if normalize(obj.get(sorter)) == list_id][0]
            compare_obj(item, nextcomp, err)
        except IndexError:
            err.append(f'No matching object for {list_id} in {clist}')


def compare_list(gold, clist, err, key=''):
    """ Help function to compare(), compares lists
        Assumes that the two lists are ordered the same way
    """
    if gold and isinstance(gold[0], dict):
        # If this is a list of objects, and we know how to sort these,
        # use the compare_objlist() instead
        sorter = config.config.SORT_BY.get(key)
        if sorter:
            compare_objlist(gold, clist, sorter, err)
            return

    for n, item in enumerate(gold):
        if len(clist) <= n:
            err.append(f'Result list too short. {item} not in {clist}')
            break
        elif isinstance(item, list):
            compare_list(sorted(item), sorted(clist[n]), err, key)
        else:
            if item not in clist:
                err.append(f'{item} not in {clist}')


def normalize(val):
    """ Normalize a value before comparison to other values
    """
    if isinstance(val, float):
        return round(val, config.config.PRECISION)
    return val
