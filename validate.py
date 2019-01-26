"""
Module responsible for validating queries and replies
Uses openapi_core to validate against the api specification
Comparisions of the status code and the result data
"""
import json
import logging
import sys
import urllib.request
import urllib.parse
import yaml

from openapi_core import create_spec
from openapi_core.shortcuts import RequestValidator, ResponseValidator
from openapi_core.wrappers.base import BaseOpenAPIRequest, BaseOpenAPIResponse
from werkzeug.datastructures import ImmutableMultiDict


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

    def open(self):
        """ Open the url """
        url = '/'.join([self.host_url, self.path.strip('/')])
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
        try:
            response = request.open()
            self.data = response.read()
            self.status_code = response.getcode()
            self.mimetype = response.info().get_content_type()

        except urllib.error.HTTPError as err:
            self.status_code = err.getcode()
            self.mimetype = err.info().get_content_type()
            self.data = err.read()


def parse_spec(inp_file):
    """ Parse a yaml file into a specification object """
    with open(inp_file) as stream:
        y_spec = yaml.load(stream)
    return create_spec(y_spec)


def validate_info(spec, host):
    """ Check that the beacon's info response is ok """
    validator = RequestValidator(spec)
    # TODO stupid handling of url, openapi_core won't accept eg
    # https://swefreq-dev.nbis.se/api/beacon-elixir/
    path = '' if host.endswith('/') else '/'
    req = BeaconRequest(host, 'GET', path)
    logging.info('Testing request...')
    result = validator.validate(req)
    print_errors(result)
    logging.info('Testing response...')
    resp = BeaconResponse(req)
    validator = ResponseValidator(spec)
    result = validator.validate(req, resp)
    print_errors(result)
    return result


def validate_call(spec, host, query, validate_query=True, code='', gold={}):
    """ Validate a query and its response """
    req = BeaconRequest(host, 'GET', 'query', args=query)
    errors = []
    if validate_query:
        # check that the query complies to the api spec
        validator = RequestValidator(spec)
        result = validator.validate(req)
        errors.extend(result.errors)
    # check that the response complies to the api spec
    resp = BeaconResponse(req)
    validator = ResponseValidator(spec)
    result = validator.validate(req, resp)
    errors.extend(result.errors)
    if code and resp.status_code != code:
        errors += [f'Unexpected http code {resp.status_code}. Expected: {code}']

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
    except AssertionError as e:
        return [str(e)]
    return []


def compare_obj(gold, obj):
    """ Help function to compare(), compares objects """
    for key, val in gold.items():
        assert key in obj, 'Value missing: %s   %s' % (key, obj.keys)
        if isinstance(val, dict):
            compare_obj(val, obj[key])
        elif isinstance(val, list):
            compare_list(val, obj[key])
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


if __name__ == "__main__":
    host_url = 'http://localhost:5050'
    if len(sys.argv) > 1:
        host_url = sys.argv[1]
    spec_file = parse_spec('beacon.yaml')
    if not validate_info(spec_file, host_url).errors:
        logging.info('No errors')
