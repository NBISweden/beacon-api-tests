"""Module responsible for validating queries and replies.

Uses jsonschemas and openapi_core to validate against the api specification, alos compares of the status code.
Gives warnings when the validation fails.
"""
import json
import logging
import urllib.request
import urllib.parse

from openapi_core.unmarshalling.schemas.exceptions import InvalidSchemaValue
from openapi_core.shortcuts import RequestValidator, ResponseValidator
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.response.datatypes import OpenAPIResponse
from werkzeug.datastructures import ImmutableMultiDict

import utils.errors as err
import utils.setup
import utils.jsonschemas


def call_beacon(path='query', query=None, ignore_schemas=False, code=200):
    """Make a query to the beacon and validate against the schemas."""
    request, response = make_query(path=path, query=query, code=code)
    if not ignore_schemas:
        validate(request, response, path, query)
    return json.loads(response.data)


def make_query(path='query', query=None, code=200):
    """Make a query to the beacon."""
    settings = utils.setup.Settings()
    query = {} if query is None else query
    req = BeaconRequest(settings.host, 'GET', path, args=query)
    resp = BeaconResponse(req)
    assert resp.status_code == code, f"Bad status code. Got {resp.status_code}, expected {code}"
    return req, resp


def validate(req, resp, path, query):
    """Validate a query and its response."""
    settings = utils.setup.Settings()
    warnings = []
    if settings.openapi:
        # check that the query complies to the api spec
        validator = RequestValidator(settings.openapi)
        result = validator.validate(req)
        settings.query_warnings += map(str, result.errors)
        warnings.extend(['OpenApi: ' + str(x) for x in result.errors])

        # check that the response complies to the api spec
        validator = ResponseValidator(settings.openapi)
        result = validator.validate(req, resp)
        settings.warnings += map(str, result.errors)
        for error in result.errors:
            if isinstance(error, InvalidSchemaValue):
                warning = f'OpenAPI:\n\tAt object {error.value}\n\t'
                warning += "\n\t".join(prettify_schemaerror(error))
                warnings.append(warning)
            else:
                warnings.append(f'OpenAPI: {str(error)}')

    if settings.use_json_schemas:
        if path != '/' and query is not None:
            # validate query against jsons schemas
            q_warns = utils.jsonschemas.validate(query, 'query', settings)
            warnings.extend(q_warns)
            settings.query_warnings += q_warns

        # validate response against jsons schemas
        warns = utils.jsonschemas.validate(resp.data, 'response', settings, path)
        warnings.extend(warns)
        settings.warnings += warns
    for warning in warnings:
        logging.warning(warning)

    return json.loads(resp.data)


class BeaconRequest(OpenAPIRequest):
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
            # catched below.
            raise
        except urllib.error.URLError as urlerr:
            logging.error('Url can not be opened: %s (%s)', url, urlerr.reason)
            raise err.BeaconTestError()
        return res


class BeaconResponse(OpenAPIResponse):
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


def make_offset(args):
    """Shift start & end position to adjust for beacons being 0-based."""
    settings = utils.setup.Settings()
    for key in ['start', 'end', 'startMin', 'startMax', 'endMin', 'endMax']:
        # The testsuite allows one based beacons as well, so check the settings
        if settings.start_pos == 1:
            if key in args and args[key] != 0:
                args[key] = args[key]+1


def prettify_schemaerror(error):
    """Render a readable string from InvalidSchemaValue errrors."""
    for serr in error.schema_errors:
        yield f"{'.'.join([str(x) for x in serr.path])} {serr.message}"
