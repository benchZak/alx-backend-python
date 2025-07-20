#!/usr/bin/env python3
"""Test module for utils.py - covers tasks 0 to 3"""

import unittest
from parameterized import parameterized
from unittest.mock import patch, Mock, PropertyMock
from utils import access_nested_map, get_json, memoize


# =============================================
# TASK 0: Test access_nested_map function
# =============================================
class TestAccessNestedMap(unittest.TestCase):
    """Test class for utils.access_nested_map - Task 0"""

    @parameterized.expand([
        # Test case 1: Access top-level key
        ({"a": 1}, ("a",), 1),
        # Test case 2: Access nested dictionary
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        # Test case 3: Access nested value
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns correct value - Task 0"""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    # =============================================
    # TASK 1: Test access_nested_map exceptions
    # =============================================
    @parameterized.expand([
        # Test case 1: Missing top-level key
        ({}, ("a",), KeyError),
        # Test case 2: Missing nested key
        ({"a": 1}, ("a", "b"), KeyError),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_exc):
        """Test that access_nested_map raises correct exceptions - Task 1"""
        with self.assertRaises(expected_exc):
            access_nested_map(nested_map, path)


# =============================================
# TASK 2: Test get_json function
# =============================================
class TestGetJson(unittest.TestCase):
    """Test class for utils.get_json - Task 2"""

    @parameterized.expand([
        # Test case 1: Simple payload
        ("http://example.com", {"payload": True}),
        # Test case 2: Different payload
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('requests.get')
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test get_json returns expected result without HTTP calls - Task 2"""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        # Call the function
        result = get_json(test_url)

        # Assertions
        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


# =============================================
# TASK 3: Test memoize decorator
# =============================================
class TestMemoize(unittest.TestCase):
    """Test class for utils.memoize - Task 3"""

    def test_memoize(self):
        """Test that memoize caches the result properly - Task 3"""
        
        class TestClass:
            """Test class for memoize testing"""
            def a_method(self):
                """Method to be memoized"""
                return 42

            @memoize
            def a_property(self):
                """Memoized property"""
                return self.a_method()

        # Patch a_method to track calls
        with patch.object(TestClass, 'a_method') as mock_method:
            # Configure mock return value
            mock_method.return_value = 42
            
            # Create instance and call property twice
            test_instance = TestClass()
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Assertions
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock_method.assert_called_once()


if __name__ == "__main__":
    unittest.main()
