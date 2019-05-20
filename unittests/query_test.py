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
        """Test smth."""
        _req, resp = utils.beacon_query.make_query(code=200)
        self.assertEqual(resp.status_code, 200)

    @patch('utils.beacon_query.BeaconRequest')
    @patch('utils.beacon_query.BeaconResponse', **{'return_value.status_code': 400})
    def test_make_bad_query(self, _beaconrequest, _beaconresponse):
        """Test smth."""
        with self.assertRaises(AssertionError):
            utils.beacon_query.make_query(code=200)

    @patch('utils.setup.Settings', **SETTINGS)
    @patch('utils.beacon_query.BeaconResponse', data='{"bad": "value"}')
    @patch('logging.warning')
    def test_validate(self, warnings, resp, _setup):
        """Test that responses not matching the schemas give warnings."""
        req = {}
        utils.beacon_query.validate(req, resp, path='', query=req)
        warnings.assert_called()

    @patch('utils.setup.Settings', **SETTINGS)
    def test_make_offset(self, _settings):
        """Test that shifting from 0-based to 1-based positions works."""
        init_obj = {'start': 22, 'startMin': 0, 'startMax': 0, 'endMin': 0, 'endMax': 0, 'end': 500, 'other': 2}
        obj = {**init_obj}
        utils.beacon_query.make_offset(obj)
        for key in init_obj:
            if key not in ['start', 'end']:
                self.assertEqual(init_obj[key], obj[key])
            else:
                self.assertNotEqual(init_obj[key], obj[key])
