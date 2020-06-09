"""Tests for the reading specifications."""
import json
import logging
import unittest
from parameterized import parameterized
from unittest.mock import patch

import utils.beacon_query
import utils.jsonschemas
import utils.run_test


MOCK_RESPONSE = {
    'return_value.status_code': 200,
    'return_value.data': json.dumps({
        "beaconId": "localhost:5050",
        "apiVersion": "1.1.0",
        "exists": True,
        "alleleRequest": {
            "referenceName": "22",
            "referenceBases": "C",
            "assemblyId": "GRCh38",
            "includeDatasetResponses": "HIT",
            "variantType": "SNP",
            "datasetIds": ["GRCh38:beacon_test:2030-01-01"],
            "start": 17302971,
            "end": 17302972
        },
        "datasetAlleleResponses": [{
            "datasetId": "GRCh38:beacon_test:2030-01-01",
            "referenceName": "22",
            "externalUrl": "",
            "note": "",
            "variantCount": 2931,
            "callCount": 5008,
            "sampleCount": 2504,
            "exists": True,
            "referenceBases": "C",
            "alternateBases": "A",
            "variantType": "SNP",
            "start": 17302971,
            "end": 17302972,
            "frequency": 0.585264027,
            "info": {"accessType": "PUBLIC"}
        }]
    })
}


def generate_failing_tests():
    """Read the test yaml, validate it agaist the schema, return the tests."""
    tests_file = 'integrationtests/test.yaml'
    schema_file = 'integrationtests/beacon_spec.yaml'
    # Since we need to use parameterized.expand, each element must be in its own tuple
    # (only tests with `expand` will be executed with unittest, according to the docs)
    return [(x,) for x in utils.jsonschemas.load_and_validate_test(tests_file, schema_file)]


class TestFullTest(unittest.TestCase):
    """Load a test and spec file, run through testing."""

    @patch('logging.error')
    @patch('utils.beacon_query.BeaconRequest')
    @patch('utils.beacon_query.BeaconResponse', **MOCK_RESPONSE)
    @patch('config.config', **{'return_value.SPEC': 'integrationtests/beacon_spec.yaml'})
    def test_pass_ok_tests(self, mock_config, mock_resp, mock_req, mock_log_error):
        """Load a test and spec file, test all the positive cases without any error being logged."""
        logging.getLogger().setLevel(logging.CRITICAL)  # hide output
        tests_file = 'integrationtests/test.yaml'
        schema_file = 'tests/schema.yaml'
        tests = utils.jsonschemas.load_and_validate_test(tests_file, schema_file)
        for test in tests:
            utils.run_test.run_test(test)
            if test['name'] == 'ok':
                mock_log_error.assert_not_called()

    @parameterized.expand(generate_failing_tests())
    def test_warn_on_exception(self, test):
        """
        Load a test and spec file, test all the negative cases.
        Make sure an error is logged for each of them.
        """
        # These tests are parameterized and run separately, to get a better idea
        # of the error in case one of them fails.
        logging.getLogger().setLevel(logging.CRITICAL)  # hide output
        # Use context managers instead of decorators to avoid bug on errors:
        # https://github.com/wolever/parameterized/issues/66
        with patch('config.config'), patch('utils.beacon_query.BeaconResponse', **MOCK_RESPONSE),\
            patch('utils.beacon_query.BeaconRequest'),patch('logging.error') as mock_log_error:
                utils.run_test.run_test(test)
                if test['name'] != 'ok':
                    mock_log_error.assert_called()
