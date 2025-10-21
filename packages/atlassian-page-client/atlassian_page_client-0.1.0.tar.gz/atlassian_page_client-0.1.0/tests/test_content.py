"""Tests for AtlassianPageContent."""

import pytest
from bs4 import BeautifulSoup
import bs4

from atlassian_page_client.content import AtlassianPageContent


class TestAtlassianPageContent:
    """Test cases for AtlassianPageContent class."""

    def test_initialization(self, sample_html_content):
        """Test content initialization."""
        content = AtlassianPageContent(sample_html_content)
        
        assert content.raw_html == sample_html_content
        assert isinstance(content.soup, BeautifulSoup)

    def test_get_root(self, sample_html_content):
        """Test get_root method."""
        content = AtlassianPageContent(sample_html_content)
        root = content.get_root()
        
        assert isinstance(root, BeautifulSoup)
        assert root == content.soup

    def test_prettify(self, sample_html_content):
        """Test prettify method."""
        content = AtlassianPageContent(sample_html_content)
        pretty_html = content.prettify()
        
        assert isinstance(pretty_html, str)
        assert len(pretty_html) > 0  # Should return non-empty string
        assert 'Test paragraph' in pretty_html

    def test_find_by_attribute_found(self, sample_html_content):
        """Test find_by_Attribute when element is found."""
        content = AtlassianPageContent(sample_html_content)
        
        # Find table by ac:local-id
        table = content.find_by_Attribute('ac:local-id', 'test-table')
        
        assert table is not None
        assert isinstance(table, bs4.element.Tag)
        assert table.name == 'table'

    def test_find_by_attribute_not_found(self, sample_html_content):
        """Test find_by_Attribute when element is not found."""
        content = AtlassianPageContent(sample_html_content)
        
        # Try to find non-existent element
        result = content.find_by_Attribute('non-existent', 'value')
        
        assert result is None

    def test_find_by_attribute_data_attribute(self, sample_html_content):
        """Test find_by_Attribute with data attributes."""
        content = AtlassianPageContent(sample_html_content)
        
        # Find div by data-test attribute
        div = content.find_by_Attribute('data-test', 'test-div')
        
        assert div is not None
        assert isinstance(div, bs4.element.Tag)
        assert div.name == 'div'
        assert 'Test div' in div.get_text()

    def test_find_by_attribute_case_sensitive(self, sample_html_content):
        """Test that find_by_Attribute is case sensitive."""
        content = AtlassianPageContent(sample_html_content)
        
        # Should not find with wrong case
        result = content.find_by_Attribute('data-test', 'TEST-DIV')
        assert result is None
        
        # Should find with correct case
        result = content.find_by_Attribute('data-test', 'test-div')
        assert result is not None

    def test_new_tag_simple(self, sample_html_content):
        """Test new_tag method with simple tag."""
        content = AtlassianPageContent(sample_html_content)
        
        new_p = content.new_tag('p')
        
        assert isinstance(new_p, bs4.element.Tag)
        assert new_p.name == 'p'
        assert new_p.string is None

    def test_new_tag_with_string(self, sample_html_content):
        """Test new_tag method with string content."""
        content = AtlassianPageContent(sample_html_content)
        
        new_p = content.new_tag('p', string='Hello World')
        
        assert isinstance(new_p, bs4.element.Tag)
        assert new_p.name == 'p'
        assert new_p.string == 'Hello World'

    def test_new_tag_with_attributes(self, sample_html_content):
        """Test new_tag method with attributes."""
        content = AtlassianPageContent(sample_html_content)
        
        new_div = content.new_tag('div', **{'class': 'test-class', 'id': 'test-id'})
        
        assert isinstance(new_div, bs4.element.Tag)
        assert new_div.name == 'div'
        assert 'test-class' in new_div.get('class', [])
        assert new_div.get('id') == 'test-id'

    def test_new_tag_complex_attributes(self, sample_html_content):
        """Test new_tag method with complex attributes."""
        content = AtlassianPageContent(sample_html_content)
        
        new_table = content.new_tag(
            'table',
            **{'ac:local-id': 'new-table', 'data-test': 'complex'}
        )
        
        assert isinstance(new_table, bs4.element.Tag)
        assert new_table.name == 'table'
        assert new_table.get('ac:local-id') == 'new-table'
        assert new_table.get('data-test') == 'complex'

    def test_content_modification_and_retrieval(self, sample_html_content):
        """Test that content modifications are reflected in the soup."""
        content = AtlassianPageContent(sample_html_content)
        
        # Add a new paragraph
        new_p = content.new_tag('p', string='Added content')
        content.soup.append(new_p)
        
        # Check that it's in the soup
        soup_str = str(content.soup)
        assert 'Added content' in soup_str

    def test_find_and_modify_element(self, sample_html_content):
        """Test finding an element and modifying it."""
        content = AtlassianPageContent(sample_html_content)
        
        # Find the test table
        table = content.find_by_Attribute('ac:local-id', 'test-table')
        assert table is not None
        
        # Add a new row
        new_row = content.new_tag('tr')
        new_cell = content.new_tag('td', string='New Cell')
        new_row.append(new_cell)
        table.append(new_row)
        
        # Verify the modification
        soup_str = str(content.soup)
        assert 'New Cell' in soup_str

    def test_empty_html_content(self):
        """Test content with empty HTML."""
        content = AtlassianPageContent("")
        
        assert content.raw_html == ""
        assert isinstance(content.soup, BeautifulSoup)

    def test_malformed_html_handling(self):
        """Test content with malformed HTML."""
        malformed_html = "<p>Unclosed paragraph<div>Nested without closing</p>"
        content = AtlassianPageContent(malformed_html)
        
        assert content.raw_html == malformed_html
        assert isinstance(content.soup, BeautifulSoup)
        # BeautifulSoup should handle malformed HTML gracefully
        assert content.soup is not None

    def test_multiple_elements_with_same_attribute(self):
        """Test finding elements when multiple have the same attribute."""
        html_with_multiple = """
        <div>
            <p class="test">First</p>
            <p class="test">Second</p>
            <p class="other">Third</p>
        </div>
        """
        content = AtlassianPageContent(html_with_multiple)
        
        # find_by_Attribute should return the first match
        result = content.find_by_Attribute('class', 'test')
        assert result is not None
        assert 'First' in result.get_text()

    def test_special_characters_in_content(self):
        """Test content with special characters."""
        html_with_special = "<p>Test with émojis 🎉 and special chars: &lt;&gt;&amp;</p>"
        content = AtlassianPageContent(html_with_special)
        
        assert content.raw_html == html_with_special
        root = content.get_root()
        assert '🎉' in str(root) or 'émojis' in str(root)
