#!/usr/bin/env python3
"""Test module for client.py - covers tasks 4 to 8"""

import unittest
from parameterized import parameterized, parameterized_class
from unittest.mock import patch, Mock, PropertyMock
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


# =============================================
# TASK 4: Test GithubOrgClient.org property
# =============================================
class TestGithubOrgClient(unittest.TestCase):
    """Test class for GithubOrgClient - Tasks 4-7"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct value - Task 4"""
        test_payload = {"org": org_name}
        mock_get_json.return_value = test_payload
        client = GithubOrgClient(org_name)
        result = client.org
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, test_payload)

    # =============================================
    # TASK 5: Test _public_repos_url property
    # =============================================
    def test_public_repos_url(self):
        """Test that _public_repos_url returns correct value - Task 5"""
        test_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
        with patch('client.GithubOrgClient.org',
                  new_callable=PropertyMock,
                  return_value=test_payload):
            client = GithubOrgClient("google")
            result = client._public_repos_url
            self.assertEqual(result, test_payload["repos_url"])

    # =============================================
    # TASK 6: Test public_repos method
    # =============================================
    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that public_repos returns correct list - Task 6"""
        test_repos = [{"name": "repo1"}, {"name": "repo2"}]
        mock_get_json.return_value = test_repos
        with patch('client.GithubOrgClient._public_repos_url',
                  new_callable=PropertyMock,
                  return_value="mock_url"):
            client = GithubOrgClient("google")
            result = client.public_repos()
            self.assertEqual(result, ["repo1", "repo2"])
            mock_get_json.assert_called_once()
            client._public_repos_url.assert_called_once()

    # =============================================
    # TASK 7: Test has_license static method
    # =============================================
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that has_license returns correct boolean - Task 7"""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


# =============================================
# TASK 8: Integration test with fixtures
# =============================================
@parameterized_class(('org_payload', 'repos_payload',
                     'expected_repos', 'apache2_repos'),
                    TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration test for GithubOrgClient - Task 8"""

    @classmethod
    def setUpClass(cls):
        """Set up class with mock patcher - Task 8"""
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()

        def side_effect(url):
            """Side effect function to return different payloads"""
            if url.endswith("/orgs/google"):
                return Mock(json=lambda: cls.org_payload)
            if url.endswith("/repos"):
                return Mock(json=lambda: cls.repos_payload)
            return None

        cls.mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Tear down class by stopping patcher - Task 8"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos with integration - Task 8"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filter - Task 8"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(license="apache-2.0"),
                         self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
