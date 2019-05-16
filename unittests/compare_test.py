"""Tests for the comparisons of the Beacon responses."""
import unittest
from unittest.mock import patch

import utils.errors as err
import utils.compare


class TestComparisons(unittest.TestCase):
    """Test comparisons."""

    def test_partly_in_wrong_key(self):
        """Test that if the response does not contain the key, an error is raised."""
        gold = {'val1': 'a', 'val2': 'b', 'val3': 'c'}
        obj = {'other': [gold]}
        with self.assertRaises(AssertionError):
            utils.compare.assert_partly_in(gold, obj, 'key')

    def test_partly_in_equal(self):
        """Test that if the response contains the gold object, no error is raised."""
        gold = {'val1': 'a', 'val2': 'b', 'val3': 'c'}
        obj = gold
        errors = []
        utils.compare.compare_obj(gold, obj, 'key')
        self.assertTrue(not errors)

    def test_partly_in_bigger(self):
        """Test that if the response contains the gold object, no error is raised."""
        gold = {'val1': 'a', 'val2': 'b', 'val3': 'c'}
        obj = {**gold, 'val4': 'd'}
        errors = []
        utils.compare.compare_obj(gold, obj, errors)
        self.assertTrue(not errors)

    def test_partly_in_wrong_value(self):
        """Test that if the response contains an bad value, an error is raised."""
        gold = {'val1': 'a', 'val2': 'b', 'val3': 'c'}
        obj = {**gold, 'val1': 'c'}
        errors = []
        utils.compare.compare_obj(gold, obj, errors)
        self.assertTrue(errors)

    def test_partly_in_wrong_type(self):
        """Test that if the response does a value of the wrong type, an error is raised."""
        gold = {'val1': 'a', 'val2': 'b', 'val3': 'c'}
        obj = {**gold, 'val1': {'a': 'a'}}
        errors = []
        utils.compare.compare_obj(gold, obj, errors)
        self.assertTrue(errors)

    def test_partly_in_smaller(self):
        """Test that if the response does a value of the wrong type, an error is raised."""
        gold = {'val1': 'a', 'val2': 'b', 'val3': 'c'}
        obj = {'val1': 'a'}
        errors = []
        utils.compare.compare_obj(gold, obj, errors)
        self.assertTrue(errors)

    def test_not_in(self):
        """Test that if the response contains the gold object, an error is raised."""
        gold = {'val1': 'a', 'val2': 'b'}
        obj = {'key': [gold]}
        with self.assertRaises(err.ResponseError):
            utils.compare.assert_not_in(gold, obj, 'key')

    def test_not_in_list(self):
        """Test that if the gold object is somewhere in the response list, an error is raised."""
        gold = {'val1': 'apa'}
        obj = {'key': [{'val1': 'tax'}, {'val1': 'apa'}]}
        with self.assertRaises(err.ResponseError):
            utils.compare.assert_not_in(gold, obj, 'key')

    def test_not_in_value(self):
        """Test that if the response contains a key with another value from the gold object, no errors are returned."""
        gold = {'val1': 'bepa'}
        obj = {'val1': 'apa'}
        errors = []
        utils.compare.not_in(obj, gold, errors)
        self.assertTrue(not errors)

    def test_not_in_forbidden_value(self):
        """Test that if the response contains a key with empty value from the gold object, an error is returned."""
        gold = {'val1': ''}
        obj = {'val1': 'apa'}
        errors = []
        utils.compare.not_in(obj, gold, errors)
        self.assertTrue(errors)

    def test_not_in_empty_value(self):
        """Test that if the response same key but another value, no errors are returned."""
        gold = {'val1': 'bepa'}
        errors = []
        utils.compare.not_in({}, gold, errors)
        self.assertTrue(not errors)

    @patch.dict('utils.compare.SORT_BY', {'key': ['sorter']})
    def test_find_matching_object(self):
        """Test that the best matching ."""
        gold = {'val1': 'bepa', 'sorter': 3}
        obj = {'key': [{'val1': 'apa', 'sorter': 0}, {'val1': 'bepa', 'sorter': 3}, {'val1': 'cepa', 'sorter': 2}]}
        res = utils.compare.find_matching_object(gold, obj, 'key')
        self.assertEqual(gold, res)


if __name__ == '__main__':
    unittest.main()
