# Validation tests for beacon api 1.0.0

This project contains tests that can be used for any Beacon implemention using api version 1.0.0.
The Beacon's responses are validated against the 
[OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml).
and against JSON schemas by [CSCfi](https://github.com/CSCfi/beacon-python/tree/master/beacon_api/schemas).
Apart from this, the counts returned by the beacon are also checked.

The project uses [openapi-core](https://github.com/p1c2u/openapi-core) and [jsonschemas](https://python-jsonschema.readthedocs.io/en/latest/)
(version 2.6 for compatability with `openapi-core`).


**To run**,
install dependencies:

`pip3 install -r requirements.txt`

Then run the tests:

`python3 run.py`

This test assumes a local server running on your machine. To test the Swedish beacon, run 

`python3 run.py --host sv`

See below for other alternatives.


## Options

**Specifying a beacon to test**

Default: use `localhost:5050`.

Other options:

- Use a host specified in `config/config.py`:

  `python3 run.py --host sv`

- Use a custom host:

  `python3 run.py --host http://beacon.com`


**Validation options**

Default: validate against the OpenAPI spec, the JSON schemas and check that the results
match (eg. that we get the correct counts).

Other options:

- `--no_openapi`  Don't validate against the OpenAPI specification

- `--no_json`    Don't validate against the JSON Schemas

- `--only_structure`  Don't validate the resulting counts, frequencies etc.


**Output options**

Default: show information, warnings and error messages.

Other options:

- `--only_warn`   Only print warnings and errors



## Using local validation schemas
The OpenAPI specification can be downloaded from
[the GA4GH's GitHub repo](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml).
To use a local version of it, specify it's path in `config/config.py`:

```
# Path to the OpenAPI spec
SPEC = 'beacon.yaml'
```

The JSON schemas can be downloaded from
[the CSCfi's  GitHub repo](https://github.com/CSCfi/beacon-python/tree/master/beacon_api/schemas).  
To use local versions, put them in a directory and specify it's path in `config/config.py`:

```
# Directory containing JSON schemas
SCHEMAS = 'schemas'
```

## Create new tests:
Create a python file and save it in the `tests` directory and put "test" in it's name, eg `tests/test_deletion.py`.

Create a function returning a test query together with a expected response.
The expected response may be partial, and the real result must be a superset of this.
The decorator `validate_query` takes the expected status code as input argument.

**Example** `tests/my_test.py`:
```py
from utils.validate import validate_query

@validate_query(200)
def test_deletion():
    """ Test variantTypes deletion """
    query = {
      'referenceName': 1,
      'referenceBases': 'CT',
      'assemblyId': 'GRCh37',
      'start': 85177351,
      'end': 85177353,
      'includeDatasetResponses': 'HIT'
      'variantType': 'DEL'
        }
    resp = {"datasetAlleleResponses":
             [{"datasetId": "GRCh37p13:SweGen:20180409",
               "referenceName": "1",
               "callCount": 2000,
               "variantCount": 1,
               "sampleCount": 1000,
               "exists": True,
               "referenceBases": "CT",
               "alternateBases": "C",
               "variantType": "DEL",
               "frequency": 0.0005
           }]}

    return query, resp
```

## Current tests:
- The `info` (`/`) endpoint aswer

- Queries that are not allowed, but cannot be formally forbidden by OpenAPI,
  eg parameter dependencies and mutual exclusivness. See `tests/beaconerrors_tests.py`.

- That the beacon does not accept queries that are not allowed according to the api spec.
  See `tests/specerrors_tests.py`

- The result counts of some specific queries. See `tests/query_tests.py`.

## TODO

#### Overall

- 0/1 based beacons. Should be 0-based, but can be set in `config/config.py` now.

- Responses from bad queries does not always match the schema (try `beaconerrors_test.py` or `specerrors_test.py`)
   (see also https://github.com/ga4gh-beacon/specification/issues/252)

- Test other type of count (eg. `call cannot be made  => .|.`)?

- How exact should the `frequency` be? Rounding to more than 6 digits, will give errors for Swe vs. Fin.
