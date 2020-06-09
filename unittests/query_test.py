"""Tests for the comparisons of the Beacon responses."""
import unittest
from unittest.mock import patch

import utils.beacon_query


JSON_RESPONSE = {
    "definitions": {},
    "type": "object",
    "additionalProperties": False,
    "required": [
        "beaconId"
    ],
    "properties": {
        "beaconId": {
            "type": "string",
            "pattern": "^(.*)$"
        },
        "apiVersion": {
            "type": "string",
            "pattern": "^(.*)$"
        },
        "exists": {
            "oneOf": [{"type": "boolean"}, {"type": "null"}]
        }
    }
}


SETTINGS = {'return_value.use_json_schemas': True, 'return_value.openapi': False,
            'return_value.json_schemas': {'response': JSON_RESPONSE},
            'return_value.start_pos': 1}


class TestQueries(unittest.TestCase):
    """Test queries and schema validation."""

    @patch('utils.beacon_query.BeaconRequest')
    @patch('utils.beacon_query.BeaconResponse', **{'return_value.status_code': 200})
    def test_make_good_query(self, _beaconresponse, _beaconrequest):
        """Test  a successfull query.

        Make sure it won't raise any error and that the status code is 200.
        """
        _req, resp = utils.beacon_query.make_query(code=200)
        self.assertEqual(resp.status_code, 200)

    @patch('utils.beacon_query.BeaconRequest')
    @patch('utils.beacon_query.BeaconResponse', **{'return_value.status_code': 400})
    def test_make_bad_query(self, _beaconrequest, _beaconresponse):
        """
        Test that an error is raised for status code 400.

        _beaconrequest is the mocked beacon request, used in make_query()
        _beaconresponse is the mocked beacon response, used in make_query()
        """
        with self.assertRaises(AssertionError):
            utils.beacon_query.make_query(code=200)

    @patch('utils.setup.Settings', **SETTINGS)
    @patch('utils.beacon_query.BeaconResponse', data='{"bad": "value"}')
    @patch('logging.warning')
    def test_validate(self, warnings, resp, _setup):
        """
        Test that responses not matching the schemas give warnings.

        warnings - is the mocked method for logging.warning, used by validate()
        resp - the mocked beacon response
        setup - the mock settings, not used here but in validate()
        """
        req = {}
        utils.beacon_query.validate(req, resp, path='', query=req)
        warnings.assert_called()

    @patch('utils.setup.Settings', **SETTINGS)
    def test_make_offset(self, _settings):
        """Test that shifting from 0-based to 1-based positions works."""
        init_obj = {'start': 22, 'startMin': 0, 'startMax': 0,
                    'endMin': 0, 'endMax': 0, 'end': 500,
                    'other': 2}
        obj = {**init_obj}  # make a copy
        utils.beacon_query.make_offset(obj)
        for key in init_obj:
            if key not in ['start', 'end']:
                # nothing else in the object is changed
                self.assertEqual(init_obj[key], obj[key])
            else:
                # the start and end positions are changed
                self.assertNotEqual(init_obj[key], obj[key])
