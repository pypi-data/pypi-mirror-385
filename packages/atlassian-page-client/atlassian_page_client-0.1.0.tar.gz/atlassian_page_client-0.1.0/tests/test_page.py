"""Tests for AtlassianPage."""

import pytest
import json
import copy

from atlassian_page_client.page import AtlassianPage
from atlassian_page_client.content import AtlassianPageContent


class TestAtlassianPage:
    """Test cases for AtlassianPage class."""

    def test_initialization(self, sample_page_data):
        """Test page initialization."""
        page = AtlassianPage("12345", sample_page_data)
        
        assert page.page_id == "12345"
        assert page.raw_content == sample_page_data
        assert isinstance(page.page_content, AtlassianPageContent)

    def test_get_page_id(self, sample_page_data):
        """Test get_page_id method."""
        page = AtlassianPage("test-id", sample_page_data)
        assert page.get_page_id() == "test-id"

    def test_get_working_page_content(self, sample_page_data):
        """Test get_working_page_content method."""
        page = AtlassianPage("12345", sample_page_data)
        content = page.get_working_page_content()
        
        assert isinstance(content, AtlassianPageContent)
        assert content.raw_html == sample_page_data['body']['storage']['value']

    def test_prettify(self, sample_page_data):
        """Test prettify method."""
        page = AtlassianPage("12345", sample_page_data)
        pretty_json = page.prettify()
        
        # Should be valid JSON
        parsed = json.loads(pretty_json)
        assert isinstance(parsed, dict)
        assert parsed['id'] == "12345"

    def test_get_page_content_dict(self, sample_page_data):
        """Test get_page_content_dict method."""
        page = AtlassianPage("12345", sample_page_data)
        content_dict = page.get_page_content_dict()
        
        assert isinstance(content_dict, dict)
        assert content_dict['id'] == "12345"
        assert 'body' in content_dict
        assert 'storage' in content_dict['body']
        assert 'value' in content_dict['body']['storage']

    def test_get_page_content_dict_preserves_modifications(self, sample_page_data):
        """Test that get_page_content_dict includes content modifications."""
        page = AtlassianPage("12345", sample_page_data)
        
        # Modify the content
        page_content = page.get_working_page_content()
        new_p = page_content.new_tag('p', string='Added paragraph')
        page_content.soup.append(new_p)
        
        # Get the content dict
        content_dict = page.get_page_content_dict()
        html_value = content_dict['body']['storage']['value']
        
        # Should include the modification
        assert 'Added paragraph' in html_value

    def test_increase_version(self, sample_page_data):
        """Test increase_version method."""
        page_data = copy.deepcopy(sample_page_data)
        page = AtlassianPage("12345", page_data)
        
        original_version = page_data['version']['number']
        original_link = page_data['version']['_links']['self']
        
        page.increase_version()
        
        # Version number should be incremented
        assert page.raw_content['version']['number'] == original_version + 1
        
        # Link should be updated
        new_link = page.raw_content['version']['_links']['self']
        assert new_link != original_link
        assert str(original_version + 1) in new_link

    def test_increase_version_multiple_times(self, sample_page_data):
        """Test increase_version called multiple times."""
        page_data = copy.deepcopy(sample_page_data)
        page = AtlassianPage("12345", page_data)
        
        original_version = page_data['version']['number']
        
        # Call increase_version multiple times
        page.increase_version()
        page.increase_version()
        page.increase_version()
        
        # Version should be incremented by 3
        assert page.raw_content['version']['number'] == original_version + 3

    def test_increase_version_updates_link_correctly(self, sample_page_data):
        """Test that increase_version updates the version link correctly."""
        page_data = copy.deepcopy(sample_page_data)
        
        # Set a specific version link format
        page_data['version']['number'] = 5
        page_data['version']['_links']['self'] = "https://example.atlassian.net/wiki/rest/api/content/12345/version/5"
        
        page = AtlassianPage("12345", page_data)
        page.increase_version()
        
        # Check the updated link
        expected_link = "https://example.atlassian.net/wiki/rest/api/content/12345/version/6"
        assert page.raw_content['version']['_links']['self'] == expected_link
        assert page.raw_content['version']['number'] == 6

    def test_page_content_independence(self, sample_page_data):
        """Test that different pages have independent content."""
        page1 = AtlassianPage("page1", copy.deepcopy(sample_page_data))
        page2 = AtlassianPage("page2", copy.deepcopy(sample_page_data))
        
        # Modify content of page1
        content1 = page1.get_working_page_content()
        new_tag = content1.new_tag('div', string='Page 1 modification')
        content1.soup.append(new_tag)
        
        # Page2 content should be unchanged
        content2_html = page2.get_page_content_dict()['body']['storage']['value']
        assert 'Page 1 modification' not in content2_html
