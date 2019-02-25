# Validation tests for beacon api 1.0.0

This project contains tests that can be used for any Beacon implemention using api version 1.
The Beacon's responses are validated against the 
[GA4GH's OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml).
and against JSON schemas by [CSCfi](https://github.com/CSCfi/beacon-python/tree/master/beacon_api/schemas).
Apart from this, the counts returned by the beacon are also checked.

The project uses [openapi-core](https://github.com/p1c2u/openapi-core) and [jsonschemas](https://python-jsonschema.readthedocs.io/en/latest/)
(version 2.6 for compatability with `openapi-core`).


## The test dataset

The tests expect the beacon to have a dataset called `GRCh38:beacon_test:2030-01-01`.
This should correspond to content of [the test vcf file](testdata). Before
testing your beacon, load this into your database.


## Running the test suite
To run, install dependencies:

`pip3 install -r requirements.txt`

Then run the tests:

`python3 beacon-api-tester.py`

This test assumes a local server running on your machine. See below for other alternatives.


## Options

**Specifying a beacon to test**

Default: use `localhost:5050`.

Other options:

- Use a host specified in `config/config.py`:

  `python3 beacon-api-tester.py --host sv`

- Use a custom host:

  `python3 beacon-api-tester.py --host http://beacon.com`


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

**Other**

Default: Beacons are 0-based.

Other options:

- `--one_based`   Test a beacon that is 1-based


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

## Current tests:
- The `info` (`/`) endpoint answer. Json validation and the dataset counts `variantCount`, `callCount` and `sampleCount`.


- Queries that are not allowed. Check that these return code `400`.
  See `tests/test_errors.py`

- The structure and counts of some specific queries. See `tests/test_counts.py`.


## Create new tests:
Create a python file and save it in the `tests` directory and put "test" in it's name, eg `tests/test_deletion.py`.

Create a function returning a test query together with a expected response.
The expected response may be partial, and the real result must be a superset of this.
The decorator `validate_query` takes the expected status code as input argument.

**Example** `tests/my_test.py`:
```py
from utils.validate import validate_query

@validate_query(200)  # expect http code 200
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


## TODO
#### Overall

- Responses from bad queries does not always match the schema (`tests/test_errors.py`)

   - `exists` will be `null` instead of `boolean` (see also https://github.com/ga4gh-beacon/specification/issues/252).

   - leaving out a required field (eg. `assemblyId`) gives answer which is also missing that field. 

- Test other type of count (eg. `call cannot be made  => .|.`)?

- How exact should the `frequency` be? Rounding to more than 6 digits, will give errors for Swe vs. Fin.

