"""  Responsible for configuration """
import argparse

import coloredlogs
from openapi_core import create_spec
import openapi_core.schema.servers.models
import yaml
import config.config


def setup():
    """ Set logging, get current host, read and configure API spec """
    coloredlogs.install(level='INFO', fmt='%(levelname)s: %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, nargs='?', default='local')
    c_args = parser.parse_args()
    host = config.config.HOSTS.get(c_args.host, config.config.HOSTS.get('local'))

    spec = parse_spec(config.config.SPEC)
    server = openapi_core.schema.servers.models.Server(host)
    spec.servers.append(server)
    return host, spec


def parse_spec(inp_file):
    """ Parse a yaml file into a specification object """
    with open(inp_file) as stream:
        y_spec = yaml.load(stream)
    return create_spec(y_spec)
