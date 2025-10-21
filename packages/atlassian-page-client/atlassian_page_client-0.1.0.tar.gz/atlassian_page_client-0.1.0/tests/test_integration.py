"""Integration tests for atlassian-page-client."""

import pytest
import json
from unittest.mock import Mock, patch

from atlassian_page_client import AtlassianPageClient, AtlassianPage, AtlassianPageContent


class TestIntegration:
    """Integration tests that test components working together."""

    @patch('atlassian_page_client.client.requests.get')
    @patch('atlassian_page_client.client.requests.put')
    def test_full_workflow_get_modify_put(self, mock_put, mock_get, client_config, sample_page_data):
        """Test the full workflow: get page, modify content, put page."""
        # Setup client
        client = AtlassianPageClient(**client_config)
        
        # Mock GET request
        get_response = Mock()
        get_response.status_code = 200
        get_response.text = json.dumps(sample_page_data)
        mock_get.return_value = get_response
        
        # Mock PUT request
        put_response = Mock()
        put_response.status_code = 200
        updated_data = sample_page_data.copy()
        updated_data['version']['number'] = sample_page_data['version']['number'] + 1
        put_response.text = json.dumps(updated_data)
        mock_put.return_value = put_response
        
        # Step 1: Get the page
        page = client.get("12345")
        assert isinstance(page, AtlassianPage)
        assert page.get_page_id() == "12345"
        
        # Step 2: Modify the content
        content = page.get_working_page_content()
        assert isinstance(content, AtlassianPageContent)
        
        # Add new content
        new_paragraph = content.new_tag('p', string='Integration test added this!')
        content.soup.append(new_paragraph)
        
        # Update the mock PUT response to include the modified content
        # This simulates the server returning the updated content
        modified_content = page.get_page_content_dict()
        updated_data['body']['storage']['value'] = modified_content['body']['storage']['value']
        put_response.text = json.dumps(updated_data)
        
        # Step 3: Update the page
        updated_page = client.put(page)
        
        # Verify the workflow
        assert mock_get.called
        assert mock_put.called
        assert isinstance(updated_page, AtlassianPage)
        
        # Verify content was modified
        final_content = updated_page.get_page_content_dict()
        html_content = final_content['body']['storage']['value']
        assert 'Integration test added this!' in html_content

    @patch('atlassian_page_client.client.requests.get')
    def test_find_and_modify_table(self, mock_get, client_config, sample_page_data):
        """Test finding a table and adding rows to it."""
        # Setup client
        client = AtlassianPageClient(**client_config)
        
        # Mock GET request
        response = Mock()
        response.status_code = 200
        response.text = json.dumps(sample_page_data)
        mock_get.return_value = response
        
        # Get the page
        page = client.get("12345")
        content = page.get_working_page_content()
        
        # Find the table by attribute
        table = content.find_by_Attribute('ac:local-id', 'test-table')
        assert table is not None
        
        # Add a new row to the table
        new_row = content.new_tag('tr')
        cell1 = content.new_tag('td', string='New Cell 1')
        cell2 = content.new_tag('td', string='New Cell 2')
        new_row.append(cell1)
        new_row.append(cell2)
        table.append(new_row)
        
        # Verify the modification
        page_dict = page.get_page_content_dict()
        html_content = page_dict['body']['storage']['value']
        assert 'New Cell 1' in html_content
        assert 'New Cell 2' in html_content

    def test_page_content_isolation(self, sample_page_data):
        """Test that modifications to one page don't affect others."""
        # Create two pages with the same data
        page1 = AtlassianPage("page1", sample_page_data.copy())
        page2 = AtlassianPage("page2", sample_page_data.copy())
        
        # Modify page1
        content1 = page1.get_working_page_content()
        new_elem = content1.new_tag('div', string='Page 1 only')
        content1.soup.append(new_elem)
        
        # Check that page2 is unaffected
        content2_dict = page2.get_page_content_dict()
        html2 = content2_dict['body']['storage']['value']
        assert 'Page 1 only' not in html2
        
        # Check that page1 has the modification
        content1_dict = page1.get_page_content_dict()
        html1 = content1_dict['body']['storage']['value']
        assert 'Page 1 only' in html1

    def test_version_management(self, sample_page_data):
        """Test version number management across operations."""
        page_data = sample_page_data.copy()
        original_version = page_data['version']['number']
        
        page = AtlassianPage("12345", page_data)
        
        # Version should start at original value
        assert page.raw_content['version']['number'] == original_version
        
        # Simulate what happens during put operation
        page.increase_version()
        assert page.raw_content['version']['number'] == original_version + 1
        
        # Version link should be updated
        version_link = page.raw_content['version']['_links']['self']
        assert str(original_version + 1) in version_link

    def test_complex_html_manipulation(self, sample_html_content):
        """Test complex HTML manipulation scenarios."""
        content = AtlassianPageContent(sample_html_content)
        
        # Find existing table
        table = content.find_by_Attribute('ac:local-id', 'test-table')
        assert table is not None
        
        # Create a complex structure
        new_row = content.new_tag('tr')
        
        # Cell with nested content
        complex_cell = content.new_tag('td')
        nested_div = content.new_tag('div', **{'class': 'nested-content'})
        nested_p = content.new_tag('p', string='Nested paragraph')
        nested_span = content.new_tag('span', string=' with span', **{'style': 'font-weight: bold'})
        
        nested_p.append(nested_span)
        nested_div.append(nested_p)
        complex_cell.append(nested_div)
        new_row.append(complex_cell)
        
        # Add to table
        table.append(new_row)
        
        # Verify the complex structure
        html_str = str(content.soup)
        assert 'nested-content' in html_str
        assert 'Nested paragraph' in html_str
        assert 'font-weight: bold' in html_str

    def test_error_handling_chain(self, client_config):
        """Test error handling propagation through the chain."""
        client = AtlassianPageClient(**client_config)
        
        # Test that client errors propagate properly
        with patch('atlassian_page_client.client.requests.get') as mock_get:
            response = Mock()
            response.status_code = 500
            response.text = "Internal Server Error"
            response.url = "http://test.com/api"
            mock_get.return_value = response
            
            with pytest.raises(Exception) as exc_info:
                client.get("test-id")
            
            assert "Failed to get page" in str(exc_info.value)
            assert "500" in str(exc_info.value)

    def test_content_preservation(self, sample_page_data):
        """Test that original content is preserved during modifications."""
        original_html = sample_page_data['body']['storage']['value']
        
        page = AtlassianPage("12345", sample_page_data)
        content = page.get_working_page_content()
        
        # Original content should be preserved
        assert content.raw_html == original_html
        assert 'Test content' in str(content.soup)
        
        # Add new content
        new_elem = content.new_tag('p', string='Additional content')
        content.soup.append(new_elem)
        
        # Both original and new content should be present
        final_html = str(content.soup)
        assert 'Test content' in final_html  # Original
        assert 'Additional content' in final_html  # New
