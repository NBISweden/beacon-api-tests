""" jsonschema validation.
Validates info objects, queries and responses.
Needs to use jsonschema v2.6.0 because of opencore_api """
import json
import logging
import os

import jsonschema
import config.config as config


def load_schema(name):
    """Load JSON schemas."""
    with open(os.path.join(config.SCHEMAS, name+'.json'), 'r') as fp:
        data = fp.read()
    return json.loads(data)


def validate(inp, inp_type, path='', error=False):
    """ Validate against a schema
    inp      - is a representation (dictionary or string) of a json object
    inp_type - is eithr `query` or `repsonse`
    path     - is the url of the query (either '/' or 'query')
    Returns a list of error messages
    """
    errs = []
    if not isinstance(inp, dict):
        try:
            inp = json.loads(inp)
        except json.decoder.JSONDecodeError:
            return [f"Input not a valid json object. {inp}"]
    if inp_type == 'response':
        # for response objects
        schemas = {'query': 'response', 'info': 'info', '': 'info'}
        schema = schemas[path.strip('/')]
    else:
        # for query objects
        schema = inp_type
    try:
        jschema = load_schema(schema)
    except FileNotFoundError:
        logging.warning('No JSON schema, not validating')
        return []
    validator = jsonschema.Draft4Validator(jschema)
    logging.info('Validate JSON to schema %s', schema)
    if error:
        adapt_to_error(jschema)
    for err in validator.iter_errors(inp, jschema):
        # join path, skipping list indices
        path = '.'.join([p for p in err.path if isinstance(p, str)])
        errs.append(f"JSON schema, field '{path}': " + err.message)
    return errs


def adapt_to_error(schema):
    """ On beacon errors (4xx), the response might differ slightly from the schemas """
    # TODO use another schema for this? or update the response schema to allow for this?
    try:
        schema['properties']['exists']['type'] = ["null", "boolean"]
    except KeyError:
        pass
