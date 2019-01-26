# Tests for beacon api 1.0.0

This setup uses [openapi-core](https://github.com/p1c2u/openapi-core) to validate
queries and answers against the Beacon's [OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml).


**To run**,
install dependencies:

`pip3 install -r requirements.txt`

Get the [Beacon OpenAPI specification](https://github.com/ga4gh-beacon/specification/blob/master/beacon.yaml)
and add it to this directory.

Then run

`python3 tests.py`

## Currently testing:
- The `info` (`/`) endpoint aswer

- Queries that are not allowed, but cannot be formally forbidden by OpenAPI,
  eg parameter dependencies and mutual exclusivness. See `tests/beaconerrors_tests.py`.

- That the beacon does not accept queries that are not allowed according to the api spec.
  See `tests/specerrors_tests.py`

- The result counts of some specific queries (**TODO** currently using SweGen dat. Change to a real test dataset).

## TODO

#### Overall
- Create a test dataset from 1000 genomes.
- General code cleanup

### Beacon api schema
1. Structure of all items using `KeyValue` changed from:

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
2. `BeaconAlleleResponse.exists` should nullable (on errors)
