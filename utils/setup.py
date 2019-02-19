"""  Responsible for configuration """
import json
import logging
import os
import urllib.error
import urllib.request

import jsonschema.exceptions
from openapi_core import create_spec
import openapi_core.schema.servers.models
import yaml

import config.config
import utils.errors as err


spec_url = 'https://raw.githubusercontent.com/ga4gh-beacon/specification/master/beacon.yaml'
response_url = 'https://raw.githubusercontent.com/CSCfi/beacon-python/master/beacon_api/schemas/response.json'
query_url = 'https://raw.githubusercontent.com/CSCfi/beacon-python/master/beacon_api/schemas/query.json'
info_url = 'https://raw.githubusercontent.com/CSCfi/beacon-python/master/beacon_api/schemas/info.json'


def singleton(cls, *args, **kw):
    """ Make a class a singleton """
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton


@singleton
class Settings():

    use_json_schemas = True
    check_result = True
    start_pos = 0
    json_schemas = {}
    openapi = None
    host = None

    def __init__(self):
        return

    def set_args(self, c_args):
        """ Set current host, read API specifications """

        if c_args.host and c_args.host in config.config.HOSTS:
            # use a known host
            self.host = config.config.HOSTS.get(c_args.host)
        elif c_args.host:
            # use a given url
            self.host = c_args.host
        else:
            # default, use local host
            self.host = config.config.HOSTS.get('local')

        self.check_result = not c_args.only_structure
        self.start_pos = int(c_args.one_based)

        if c_args.no_openapi:
            spec_path = ''
        else:
            if config.config.SPEC:
                logging.info('Using Beacon specification in %s', config.config.SPEC)
                spec_path = config.config.SPEC
                with open(spec_path) as stream:
                    self.openapi = parse_spec(stream)
            else:
                logging.info('Downloading Beacon specification')
                try:
                    spec_path = urllib.request.urlopen(spec_url).read()
                    self.openapi = parse_spec(spec_path)
                except urllib.error.URLError:
                    logging.warning('Could not download %s.'
                                    'Will not validate against the OpenAPI Specification.',
                                    spec_url)
                    spec_path = ''

        if spec_path:
            server = openapi_core.schema.servers.models.Server(self.host)
            self.openapi.servers.append(server)

        if c_args.no_json:
            self.use_json_schemas = False
        else:
            if config.config.SCHEMAS:
                logging.info('Using JSON schemas in %s', config.config.SCHEMAS)
                self.json_schemas['response'] = load_local_schema('response')
                self.json_schemas['query'] = load_local_schema('query')
                self.json_schemas['info'] = load_local_schema('info')
            else:
                logging.info('Downloading JSON schemas')
                load_url = lambda x: json.loads(urllib.request.urlopen(x).read())
                self.json_schemas['response'] = load_url(response_url)
                self.json_schemas['query'] = load_url(query_url)
                self.json_schemas['info'] = load_url(info_url)
        logging.info('\n')


def load_local_schema(name):
    """Load JSON schemas."""
    with open(os.path.join(config.config.SCHEMAS, name+'.json'), 'r') as fp:
        data = fp.read()
    return json.loads(data)


def parse_spec(inp_file):
    """ Parse a yaml file into a specification object """
    try:
        y_spec = yaml.load(inp_file)
        spec = create_spec(y_spec)
    except jsonschema.exceptions.RefResolutionError:
        logging.error("Could not load specification. Check your network or try again")
        raise err.BeaconTestError()
    return spec
