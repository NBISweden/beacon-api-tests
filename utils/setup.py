"""Responsible for configuration."""
import json
import logging
import os
import urllib.error
import urllib.request

import jsonschema.exceptions as json_exceptions
import openapi_core.schema.servers.models
import openapi_spec_validator.exceptions as spec_exceptions
import yaml
from openapi_core import create_spec

import config.config
import utils.errors as err
import utils.jsonschemas


VERSIONS = {'v101': {'ga4gh': 'v1.0.1', 'CSCfi': 'v1.1.0-rc1'},
            'v110': {'ga4gh': 'develop', 'CSCfi': 'v1.3.0-rc0'}
            }


SPEC_URL = 'https://raw.githubusercontent.com/ga4gh-beacon/specification/{version}/beacon.yaml'
JSON_URL = 'https://raw.githubusercontent.com/CSCfi/beacon-python/{version}/beacon_api/schemas/{querytype}.json'


def singleton(cls, *args, **kw):
    """Make a class a singleton."""
    instances = {}

    def _singleton():
        """Find existing instance."""
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


@singleton
class Settings():
    """Object containing all settings for the test suite."""

    use_json_schemas = True
    check_result = True
    start_pos = 0
    json_schemas = {}
    openapi = None
    host = None
    version = None
    errors = 0
    warnings = []
    query_warnings = []
    tests = []

    def __init__(self):
        """Initialize."""
        return

    def set_args(self, c_args):
        """Set current host, read API specifications."""
        if c_args.host and c_args.host in config.config.HOSTS:
            # use a known host
            self.host = config.config.HOSTS.get(c_args.host)
        elif c_args.host:
            # use a given url
            self.host = c_args.host
        else:
            # default, use local host
            self.host = config.config.HOSTS.get('local')

        for pathname in c_args.test:
            self.tests += utils.jsonschemas.load_and_validate_test(pathname)

        self.check_result = not c_args.only_structure
        self.start_pos = int(c_args.one_based)

        self.version = c_args.version.replace('.', '')
        spec_versions = VERSIONS[self.version]
        if c_args.no_openapi:
            spec_path = ''
        else:
            spec_path = get_spec_content(spec_versions)

        if spec_path:
            self.openapi = parse_spec(spec_path)
            server = openapi_core.schema.servers.models.Server(self.host)
            self.openapi.servers.append(server)

        if c_args.no_json:
            self.use_json_schemas = False
        else:
            if os.path.isdir(config.config.SCHEMAS):
                logging.info('Using JSON schemas in %s', config.config.SCHEMAS)
                self.json_schemas['response'] = load_local_schema('response')
                self.json_schemas['query'] = load_local_schema('query')
                self.json_schemas['info'] = load_local_schema('info')
            else:
                logging.info('Downloading JSON schemas')

                def load_url(qtype):
                    path = JSON_URL.format(querytype=qtype, version=spec_versions['CSCfi'])
                    return json.loads(urllib.request.urlopen(path).read())

                self.json_schemas['response'] = load_url('response')
                self.json_schemas['query'] = load_url('query')
                self.json_schemas['info'] = load_url('info')
        logging.info('\n')


def get_spec_content(versions):
    """
    Try to read the spec and return its content.

    Strategy:
    1. If there is a file path in the config, try read and return it.
    2. If there is a url in the config, try load and return it.
    3. Try to load the default url and return it.
    4. Return an empty string.
    """
    if not config.config.SPEC:
        return load_default_spec(versions)

    if os.path.isfile(config.config.SPEC):
        logging.info('Using Beacon specification in %s', config.config.SPEC)
        return open(config.config.SPEC)
    try:
        logging.info(f'Requesting spec {config.config.SPEC}')
        return urllib.request.urlopen(config.config.SPEC).read()
    except urllib.error.URLError:
        logging.warning(f'Could not open {config.config.SPEC}')
        return load_default_spec(versions)


def load_default_spec(versions):
    """Download the default api spec."""
    logging.info('Downloading default Beacon specification')
    try:
        spec_url = SPEC_URL.format(version=versions['ga4gh'])
        return urllib.request.urlopen(spec_url).read()
    except urllib.error.URLError:
        logging.warning('Could not download %s. '
                        'Will not validate against the OpenAPI Specification.',
                        spec_url)
        return ''


def load_local_schema(name):
    """Load JSON schemas."""
    with open(os.path.join(config.config.SCHEMAS, name+'.json'), 'r') as fp:
        data = fp.read()
    return json.loads(data)


def parse_spec(inp_file):
    """Parse a yaml file into a specification object."""
    try:
        y_spec = yaml.load(inp_file, Loader=yaml.SafeLoader)
        spec = create_spec(y_spec)
    except json_exceptions.RefResolutionError:
        logging.error("Could not load specification. Check your network or try again")
        raise err.BeaconTestError()
    except spec_exceptions.OpenAPIValidationError as specerr:
        logging.error(f"Error in specificaton: {specerr}")
        logging.error("Could not read specification. Check that your file is valid")
        raise err.BeaconTestError()
    except Exception as exc:
        logging.error('Could not read specification, unknown error:')
        logging.exception(exc)
        raise err.BeaconTestError()

    return spec
