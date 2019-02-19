""" jsonschema validation.
Validates info objects, queries and responses.
Needs to use jsonschema v2.6.0 because of opencore_api """
import json
import logging

import jsonschema


def validate(inp, inp_type, settings, path='', error=False):
    """ Validate against a schema
    inp      - is a representation (dictionary or string) of a json object
    inp_type - is eithr `query` or `repsonse`
    settings - is an object containing schemas and specs
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
        jschema = settings.json_schemas[schema]

    except KeyError:
        logging.warning('No JSON schema for %s, not validating', schema)
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
