# Validation tests for Beacon API

This project contains tests that can be used for any Beacon implemention using api version 1.0.1 and 1.1.0.
The Beacon's responses are validated against the 
[GA4GH's OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml)
and against JSON schemas by [CSCfi](https://github.com/CSCfi/beacon-python/tree/master/beacon_api/schemas).
Apart from this, the values returned by the beacon are also checked.

The project uses [openapi-core](https://github.com/p1c2u/openapi-core) and [jsonschemas](https://python-jsonschema.readthedocs.io/en/latest/).

<!-- To be updated: A few slides giving some examples can be found [here](https://nbisweden.github.io/beacon-api-tests/).-->



## Running the test suite
> Requirements: `python3` and `pip3`.

To run, install dependencies:

`pip3 install -r requirements.txt`

Then run tests from a test file: 

`python3 beacon_api_tester.py --host http://localhost:5050 --test tests/test-v101-variants.yaml`

This assumes that you have a beacon running on the `host` specified. The beacon should contain the test data
specified in the tests. By running

`python3 beacon_api_tester.py --show_data_files tests/test-v101-variants.yaml`

you can see the file names containing the data needed. See more about test data below.


### Test data

Each test specifies which data is assumes, in the field `beacondata`.

Currently, all test data is found in [testdata.csv](tests/testdata.csv) (v101)
and [testdata_mate.csv](tests/testdata_mate.csv) (v110).  The data is given in
comma separated format.


## Current tests:
- v1.0.1:
  - The `info` (`/`) endpoint answer. Json validation and the datasets in the answer.

  - Queries that are not allowed. Check that these return code `400`.
    See `tests/v101/test_errors.py`

  - The structure and answers of some specific queries. See `tests/test-v101-variants.yaml`.

  - Having multiple datasets.

- v1.1.0:
  - Structural variants (breakends)

## Create or inspect tests:
To create more tests, see [adding_tests.md](docs/adding_tests.md).
This file also gives more information on how to interpret each given test file.
Contributions (in the form of pull requests) are very welcome!


# More options
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

- `--one_based`  Test a beacon that is 1-based


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
