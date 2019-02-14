"""  Responsible for configuration """
import argparse
import json
import logging
import os
import urllib.error
import urllib.request

import coloredlogs
from openapi_core import create_spec
import openapi_core.schema.servers.models
import yaml

import config.config

spec_url = 'https://raw.githubusercontent.com/ga4gh-beacon/specification/master/beacon.yaml'
response_url = 'https://raw.githubusercontent.com/CSCfi/beacon-python/master/beacon_api/schemas/response.json'
query_url = 'https://raw.githubusercontent.com/CSCfi/beacon-python/master/beacon_api/schemas/query.json'
info_url = 'https://raw.githubusercontent.com/CSCfi/beacon-python/master/beacon_api/schemas/info.json'


def singleton(cls, *args, **kw):
   instances = {}
   def _singleton():
      if cls not in instances:
           instances[cls] = cls(*args, **kw)
      return instances[cls]
   return _singleton


@singleton
class Settings():

    openapi = None
    json_schemas = {}
    host = None


    def __init__(self):
        """ Set logging, get current host, read and configure API spec """
        coloredlogs.install(level='INFO', fmt='%(levelname)s: %(message)s')
        parser = argparse.ArgumentParser()
        parser.add_argument('host', type=str, nargs='?', default='local')
        c_args = parser.parse_args()
        self.host = config.config.HOSTS.get(c_args.host, config.config.HOSTS.get('local'))

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

        if config.config.SCHEMAS:
            logging.info('Using JSON schemas in %s', config.config.SCHEMAS)
            self.json_schemas['response'] = load_local_schema('response')
            self.json_schemas['query'] = load_local_schema('query')
            self.json_schemas['info'] = load_local_schema('info')
        else:
            logging.info('Downloading JSON schemas')
            self.json_schemas['response'] = json.loads(urllib.request.urlopen(response_url).read())
            self.json_schemas['query'] = json.loads(urllib.request.urlopen(query_url).read())
            self.json_schemas['info'] = json.loads(urllib.request.urlopen(info_url).read())




def load_local_schema(name):
    """Load JSON schemas."""
    with open(os.path.join(config.config.SCHEMAS, name+'.json'), 'r') as fp:
        data = fp.read()
    return json.loads(data)


def parse_spec(inp_file):
    """ Parse a yaml file into a specification object """
    y_spec = yaml.load(inp_file)
    return create_spec(y_spec)
