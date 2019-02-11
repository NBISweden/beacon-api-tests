# Tests for beacon api 1.0.0

This setup uses [openapi-core](https://github.com/p1c2u/openapi-core) to validate
queries and answers against the Beacon's [OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml).


**To run**,
install dependencies:

`pip3 install -r requirements.txt`

Get the [Beacon OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml)
and add it to this directory.

To verify against JSON schemas by CSCfi, download [these](https://github.com/CSCfi/beacon-python/tree/master/beacon_api/schemas) and
save them in a directory `schemas`.

Then run a chosen set of tests:

`python3 tests/beaconerror_tests.py`

This will test a local server running on your machine. To test the Swedish beacon, run 

`python3 tests/beaconerror_tests.py sv`

See `config/hosts.py` for other alternatives.

Other tests:
`python3 tests/specerror_tests.py`

`python3 tests/query_tests.py`

`python3 tests/query_fi.py`



## Create new tests:
Create a python file with a function returning a test query together with a expected response.
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
      'variantType']: 'DEL'
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
  (**TODO** currently using SweGen dat. Change to a real test dataset).

- The result counts of some specific queries for the finnish beacon. See `tests/query_fi.py`.
  (**TODO** for testing the testing only. Change to a real test dataset).

## TODO

#### Overall

- 0/1 based beacons? Can be set in `config/config.py` now.

- Responses from bad queries does not always match the schema (try `beaconerrors_test.py` or `specerrors_test.py`)
   (see also https://github.com/ga4gh-beacon/specification/issues/252)

- Test other type of count (eg. `call cannot be made  => .|.`)?

- Now using JSON schemas from CSCfi, how to link/refer properly?

- How exact should the `frequency` be? Rounding to more than 6 digits, will give errors for Swe vs. Fin.

- Make sure the result we expect follow the specification [here](https://github.com/ga4gh-beacon/specification/wiki/Calculating-counters-in-BeaconDatasetAlleleResponse).


#### Finnish vs. Swedish
- Not always the same variantType (DEL/INS)

- Different `callCount` vs. `sampleCount`


### Beacon api schema
1. Structure of all items using `KeyValue` changed from:
 **TODO** API changed in the the `develop` branch

```
    info:
      description: 'Additional structured metadata, key-value pairs.'
      type: array
      items:
         $ref: '#/components/schemas/KeyValuePair'

    KeyValuePair:
      type: object
      required:
        - key
        - value
      properties:
        key:
          type: string
        value:
          type: string
```
 to:

   ```
    info:
      description: 'Additional structured metadata, key-value pairs.'
      $ref: '#/components/schemas/KeyValuePair'

    KeyValuePair:
      type: object
      additionalProperties:
        type: string
   ```

2.  (**TODO** check if there is any issue/PR on this) `BeaconAlleleResponse.exists` should nullable (on errors)
