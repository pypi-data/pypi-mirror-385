"""Tests for AtlassianPageClient."""

import pytest
import json
import copy
from unittest.mock import Mock, patch
from requests.auth import HTTPBasicAuth

from atlassian_page_client.client import AtlassianPageClient
from atlassian_page_client.page import AtlassianPage


class TestAtlassianPageClient:
    """Test cases for AtlassianPageClient class."""

    def test_initialization(self, client_config):
        """Test client initialization."""
        client = AtlassianPageClient(**client_config)
        
        assert client.email == client_config["email"]
        assert client.token == client_config["token"]
        assert client.base_url == client_config["base_url"]
        assert isinstance(client.basicAuth, HTTPBasicAuth)
        assert client.HEADERS == {'Content-Type': 'application/json;charset=iso-8859-1'}

    def test_check_response_success(self, client_config, mock_requests_response):
        """Test check_response with successful response."""
        client = AtlassianPageClient(**client_config)
        mock_requests_response.status_code = 200
        
        # Should not raise an exception
        client.check_response(mock_requests_response)

    def test_check_response_failure(self, client_config, mock_requests_response):
        """Test check_response with failed response."""
        client = AtlassianPageClient(**client_config)
        mock_requests_response.status_code = 404
        mock_requests_response.text = "Not Found"
        
        with pytest.raises(Exception) as exc_info:
            client.check_response(mock_requests_response)
        
        assert "Failed to get page from url" in str(exc_info.value)
        assert "404" in str(exc_info.value)
        assert "Not Found" in str(exc_info.value)

    @patch('atlassian_page_client.client.requests.get')
    def test_get_page_success(self, mock_get, client_config, sample_page_data, mock_requests_response):
        """Test successful page retrieval."""
        client = AtlassianPageClient(**client_config)
        
        # Setup mock response
        mock_requests_response.status_code = 200
        mock_requests_response.text = json.dumps(sample_page_data)
        mock_get.return_value = mock_requests_response
        
        # Call the method
        page = client.get("12345")
        
        # Verify the request
        expected_url = client.base_url + "/wiki/rest/api/content/12345?expand=body.storage,version"
        mock_get.assert_called_once_with(
            expected_url,
            headers=client.HEADERS,
            auth=client.basicAuth
        )
        
        # Verify the result
        assert isinstance(page, AtlassianPage)
        assert page.get_page_id() == "12345"

    @patch('atlassian_page_client.client.requests.get')
    def test_get_page_failure(self, mock_get, client_config, mock_requests_response):
        """Test failed page retrieval."""
        client = AtlassianPageClient(**client_config)
        
        # Setup mock response for failure
        mock_requests_response.status_code = 404
        mock_requests_response.text = "Page not found"
        mock_get.return_value = mock_requests_response
        
        # Should raise an exception
        with pytest.raises(Exception):
            client.get("nonexistent")

    @patch('atlassian_page_client.client.requests.put')
    def test_put_page_success(self, mock_put, client_config, sample_page_data, mock_requests_response):
        """Test successful page update."""
        client = AtlassianPageClient(**client_config)
        
        # Create a page object
        page = AtlassianPage("12345", copy.deepcopy(sample_page_data))
        original_version = page.raw_content['version']['number']
        
        # Setup mock response for PUT
        # The put method will increment the version, so we need to account for that
        updated_data = copy.deepcopy(sample_page_data)
        updated_data['version']['number'] = original_version + 1  # This should match what increase_version() sets
        updated_data['version']['_links']['self'] = updated_data['version']['_links']['self'].replace(
            f"/{original_version}", f"/{original_version + 1}"
        )
        mock_requests_response.status_code = 200
        mock_requests_response.text = json.dumps(updated_data)
        mock_put.return_value = mock_requests_response
        
        # Call the method
        updated_page = client.put(page)
        
        # Verify the request
        expected_url = client.base_url + "/wiki/rest/api/content/12345"
        mock_put.assert_called_once()
        call_args = mock_put.call_args
        
        assert call_args[0][0] == expected_url
        assert call_args[1]['headers'] == client.HEADERS
        assert call_args[1]['auth'] == client.basicAuth
        
        # Verify the page version was incremented (put() calls increase_version())
        assert page.raw_content['version']['number'] == original_version + 1
        
        # Verify the result
        assert isinstance(updated_page, AtlassianPage)
        assert updated_page.get_page_id() == "12345"

    @patch('atlassian_page_client.client.requests.put')
    def test_put_page_failure(self, mock_put, client_config, sample_page_data, mock_requests_response):
        """Test failed page update."""
        client = AtlassianPageClient(**client_config)
        
        # Create a page object
        page = AtlassianPage("12345", sample_page_data.copy())
        
        # Setup mock response for failure
        mock_requests_response.status_code = 403
        mock_requests_response.text = "Forbidden"
        mock_put.return_value = mock_requests_response
        
        # Should raise an exception
        with pytest.raises(Exception):
            client.put(page)
