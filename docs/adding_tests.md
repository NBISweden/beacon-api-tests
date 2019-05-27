# Contributing

## Writing tests

Create a python file and save it in the `tests` directory, in the directory matching it's intended version.
Make sure that "test" is included in it's name, eg. `tests/v101/test_deletion.py`.

Create a function decorated with `run_test()`.
The expected response may be partial, and the real result must be a superset of this.

**Example** `tests/v101/my_test.py`:
```py
from utils.beacon_query import call_beacon
from utils.compare import assert_partly_in, run_test


@run_test()
def test_deletion():
    """Test variantTypes DEL."""
    query = {
      'referenceName': "1",
      'referenceBases': 'CT',
      'assemblyId': 'GRCh37',
      'start': 85177351,
      'end': 85177353,
      'includeDatasetResponses': 'HIT'
      'variantType': 'DEL'
    }
    query['start'] = 16497140
    query['end'] = 16497143
    query['referenceBases'] = 'CTT'
    query['alternateBases'] = 'C'
    # This will make a call to the beacon, validate the response to the schemas,
    # and verify that the status code is 200.
    resp = call_beacon(query=query)
    # Describe your expected result
    gold = {"datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "callCount": 5008,
            "variantCount": 4,
            "sampleCount": 2504,
            "referenceBases": "CTT",
            "alternateBases": "C",
            "variantType": "DEL",
            "frequency": 0.000798722
            }
    assert resp['exists'], 'Beacon did not find any match'
    # Assert that the gold result is included in the response (allowing for additional fields)
    assert_partly_in(gold, resp, 'datasetAlleleResponses')


@run_test()
def no_alternate():
    """Check that either alternateBases or variantType is required."""
    query = {
      'referenceName': "1",
      'referenceBases': 'CT',
      'assemblyId': 'GRCh37',
      'start': 85177351,
      'end': 85177353,
      'includeDatasetResponses': 'HIT'
    }
    # Change the expected status code, and don't validate the query or the response to the schemas
    call_beacon(query=query, code=400, ignore_schemas=True)


```

## Unit testing

Run `python -m unittest unittests/*py`
