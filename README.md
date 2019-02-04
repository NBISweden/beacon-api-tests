# Tests for beacon api 1.0.0

This setup uses [openapi-core](https://github.com/p1c2u/openapi-core) to validate
queries and answers against the Beacon's [OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml).


**To run**,
install dependencies:

`pip3 install -r requirements.txt`

Get the [Beacon OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml)
and add it to this directory.

Then run a chosen set of tests:

`python3 tests/beaconerror_tests.py`

This will test a local server running on your machine. To test the swedish beacon, run 

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
- Create a test dataset from 1000 genomes.
- General code cleanup
- Better comparisons of responses

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
