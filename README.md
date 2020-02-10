# Validation tests for Beacon API

This project contains tests that can be used for any Beacon implemention using api version 1.0.1 and 1.1.0.
The Beacon's responses are validated against the 
[GA4GH's OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml)
and against JSON schemas by [CSCfi](https://github.com/CSCfi/beacon-python/tree/master/beacon_api/schemas).
Apart from this, the counts returned by the beacon are also checked.

The project uses [openapi-core](https://github.com/p1c2u/openapi-core) and [jsonschemas](https://python-jsonschema.readthedocs.io/en/latest/).

A few slides giving some examples can be found [here](https://nbisweden.github.io/beacon-api-tests/).



## The testdata

### v101
The tests expect the beacon to have a dataset called `GRCh38:beacon_test:2030-01-01`.
This should correspond to content of [the test csv file](tests/testdata.csv).
Before testing your beacon, load this into your database.
To test multiple datasets, also load the same vcf file into a dataset called `GRCh38:beacon_test2:2030-01-01`.

### v110
To test version v110, load the structural variants from
[testdata_mate.csv](tests/testdata_mate.csv) into the main dataset (`GRCh38:beacon_test:2030-01-01`).


## Running the test suite
To run, install dependencies:

`pip3 install -r requirements.txt`

Then run the tests:

`python3 beacon_api_tester.py`

This test assumes a local server running on your machine. See below for other alternatives.


## Options

**Specifying a beacon to test**

Default: use `localhost:5050`.

Other options:

- Use a host specified in `config/config.py`:

  `python3 beacon_api_tester.py --host sv`

- Use a custom host:

  `python3 beacon_api_tester.py --host http://beacon.com`


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
- v1.0.1:
  - The `info` (`/`) endpoint answer. Json validation and the datasets in the answer.
  
  - Queries that are not allowed. Check that these return code `400`.
    See `tests/v101/test_errors.py`
  
  - The structure and answers of some specific queries. See `tests/test-v101-counts.yaml`.
  
  - Having multiple datasets.

- v1.1.0:
  - Structural variants (breakends)

## Create new tests:
To create more tests, see [adding_tests.md](docs/adding_tests.md).
Contributions (in the form of pull requests) are very welcome!
