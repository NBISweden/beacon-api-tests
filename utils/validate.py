"""Module responsible for validating queries and replies.

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
import utils.errors as err
import utils.setup
import utils.jsonschemas


def exclude_from_response(path='query'):
    """Decorator for testing that a queries response does not contain forbidden values.

    A function decorated with this should return a
    query (dict) and an dictionary with forbidden values (dict)
    """
    def decorator(func):
        query, exclude = func()
        logging.info('Testing %s\n      %s', func.__name__, func.__doc__.strip())
        errs, warns = validate_excluded(path, query, exclude)
        if errs or warns:
            logging.error('\n      Test "%s" did not pass: """%s"""', func.__name__, func.__doc__.strip())
        for error in errs:
            logging.error(error)
        for warn in warns:
            logging.warning(warn)
        logging.info('Done\n')
    return decorator


def validate_query(code, path='query', test_query=False):
    """Decorator for test queries.

    A function decorated with this should return a
    query (dict) and an expected result (dict)
    """
    def decorator(func):
        query, resp = func()
        logging.info('Testing %s\n      %s', func.__name__, func.__doc__.strip())
        errs, warns = validate_call(path, query,
                                    test_query=test_query,
                                    code=code, gold=resp)
        if errs or warns:
            logging.error('\n      Test "%s" did not pass: """%s"""', func.__name__, func.__doc__.strip())
        for error in errs:
            logging.error(error)
        for warn in warns:
            logging.warning(warn)
        logging.info('Done\n')
    return decorator


class BeaconRequest(BaseOpenAPIRequest):
    """Wrapper for a Request.

    The url can be opened using the open method
    """

    def __init__(self, host, method, path, args=None,
                 view_args=None, headers=None, data=None,
                 mimetype='application/json'):
        """Set up a Request object."""
        make_offset(args)
        self.host_url = host
        self.path = path
        self.path_pattern = path
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
        """Get the full url."""
        url = '/'+self.path_pattern
        if url.endswith('//'):
            url = url[:-1]
        return url

    def open(self):
        """Open the url."""
        url = '/'.join([self.host_url, self.path_pattern])
        if url.endswith('//'):
            url = url[:-1]
        query = urllib.parse.urlencode(self.parameters['query'])
        if query:
            url += f'?{query}'
        logging.info('Open %s', url)
        try:
            res = urllib.request.urlopen(url)
        except ValueError:
            logging.error('Url can not be opened: %s', url)
            raise err.BeaconTestError()
        except urllib.error.HTTPError:
            # HTTPErrorr are passed on to BeaconResponse.
            # Catch them here, since they are a subclass of URLError,
            # but needs to be treated separately from other types of URLErrors
            # catche below.
            raise
        except urllib.error.URLError as urlerr:
            logging.error('Url can not be opened: %s (%s)', url, urlerr.reason)
            raise err.BeaconTestError()
        return res


class BeaconResponse(BaseOpenAPIResponse):
    """Wrapper for a Response.

    Stores the response body, error code and the content type
    """

    def __init__(self, request):
        """Set up a response object."""
        self.error = False
        try:
            response = request.open()
            self.data = response.read()
            self.status_code = response.getcode()
            self.mimetype = response.info().get_content_type()

        except urllib.error.HTTPError as error:
            self.status_code = error.getcode()
            self.mimetype = error.info().get_content_type()
            self.data = error.read()
            self.error = True


def validate_call(path, query, test_query=True, code='', gold=None):
    """Validate a query and its response."""
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
        error = compare(gold, json.loads(resp.data))
        errors.extend(error)
    return errors, warnings


def make_offset(args):
    """Shift start & end position to adjust for beacons being 0-based."""
    settings = utils.setup.Settings()
    for key in ['start', 'end', 'startMin', 'startMax', 'endMin', 'endMax']:
        # The testsuite allows one based beacons as well, so check the settings
        if settings.start_pos == 1:
            if key in args:
                args[key] = max(args[key]-1, 0)


def compare(gold, obj):
    """Compare two objects to see that everything in the gold object is also in the other."""
    errs = []
    compare_obj(gold, obj, errs)
    return errs


def compare_obj(gold, obj, errors):
    """Help function to compare(), compares objects."""
    for key, val in gold.items():
        if key not in obj:
            errors.append(f'Value missing: {key}  {obj.keys()}')
            continue
        if isinstance(val, dict):
            compare_obj(val, obj[key], errors)
        elif isinstance(val, list):
            compare_list(val, obj[key], errors, key)
        else:
            if normalize(val) != normalize(obj[key]):
                errors.append(f'Bad value {key}: {val} != {obj[key]}')


def compare_list(gold, clist, errors, key=''):
    """
    Help function to compare(), compares lists.

    Assumes that the two lists are ordered the same way.
    """
    if gold and isinstance(gold[0], dict):
        # If this is a list of objects, and we know how to sort these,
        # use the compare_objlist() instead
        sorter = config.config.SORT_BY.get(key)
        if sorter:
            compare_objlist(gold, clist, sorter, errors)
            return

    for n, item in enumerate(gold):
        if len(clist) <= n:
            errors.append(f'Result list too short. {item} not in {clist}')
            break
        elif isinstance(item, list):
            compare_list(sorted(item), sorted(clist[n]), errors, key)
        else:
            if item not in clist:
                errors.append(f'{item} not in {clist}')


def compare_objlist(gold, clist, sorters, errors):
    """
    Help function to compare(), compares a list of objects.

    The objects with the (most) matching sort keys objects are compared to each other
    """
    def find_best_match(alist):
        """Sort by fst (identifier), return snd (an object)."""
        if not alist:
            return {}
        return sorted(alist, key=lambda x: x[0])[0][1]

    def get_sort_ids(obj):
        """Sort by normalized key."""
        return [normalize(obj.get(sorter)) for sorter in sorters]

    def compare_identifiers(gold, cmp):
        """Compare to objects by a given set of identifiers. Return the number of mismatches."""
        gold_id = get_sort_ids(gold)
        cmp_id = get_sort_ids(cmp)
        if gold_id == cmp_id:
            return 0
        return len([1 for (g, c) in zip(gold_id, cmp_id) if g != c])

    for golditem in gold:
        if not clist:
            errors.append(f'Too few elements, could not find {gold}')
            return
        nextcomp = find_best_match([(compare_identifiers(golditem, obj), obj) for obj in clist])
        compare_obj(golditem, nextcomp, errors)
        clist.remove(nextcomp)


def normalize(val):
    """Normalize a value before comparison to other values."""
    if isinstance(val, float):
        return round(val, config.config.PRECISION)
    return val


def validate_excluded(path, query, exclude):
    """Validate that the response does include any forbidden values."""
    settings = utils.setup.Settings()
    req = BeaconRequest(settings.host, 'GET', path, args=query)
    errors, warnings = [], []

    resp = BeaconResponse(req)
    result = json.loads(resp.data)
    not_in(result, exclude, errors)
    return errors, warnings


def not_in(obj, exclude, errors):
    """Recurse through the object of forbidden values to verify that they are not present."""
    for key in exclude.keys():
        if key not in obj:
            # key is excluded in obj -> ok
            continue

        elif not exclude[key]:
            # empty value in `exclude` -> the key is not accepted
            errors.append(f'Key {key} not allowed in answer')

        elif isinstance(exclude[key], dict):
            # go deeper
            not_in(obj[key], exclude[key], errors)

        elif isinstance(exclude[key], list):
            # check that all values in the list are excluded
            for k in exclude[key]:
                if isinstance(k, dict):
                    for item in obj[key]:
                        not_in(item, k, errors)
                if k in obj[key]:
                    errors.append(f'Value {k} not allowed in answer')

        elif obj[key] == exclude[key]:
            # equal values -> not ok
            errors.append(f'Value {{{key}: {obj[key]}}} not allowed in answer')
